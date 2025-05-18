import requests
import time
from typing import Optional, List
from logger_setup import logger
from config import COMMON_HEADERS, COOKIES
from bilibili_models import BilibiliHistoryItem
from datetime import datetime, timezone

# 自定义等待时间（秒），可根据需求调整
REQUEST_DELAY = 0.5
today = datetime.now(timezone.utc)
today_str = today.strftime("%Y%m%d")


def _log_response(name: str, response: requests.Response):
    logger.info(f"{name} Status Code: {response.status_code}")
    logger.debug(f"{name} Headers: {response.request.headers}")
    logger.debug(f"{name} Body: {response.text[:500]}...")


def make_request(method: str, url: str, headers=None, cookies=None, params=None, name: str = "request") -> Optional[
    requests.Response]:
    """
    封装 requests 请求，统一添加日志和延迟。
    :param method: 请求方法，'get' 或 'post' 等
    :param url: 请求 URL
    :param headers: 请求头
    :param cookies: Cookies
    :param params: 查询参数
    :param name: 请求名称，用于日志记录
    :return: requests.Response 对象，如果失败返回 None
    """
    try:
        if method.lower() == 'get':
            res = requests.get(url, headers=headers, cookies=cookies, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")

        _log_response(name, res)
        # 请求完成后等待一段时间
        time.sleep(REQUEST_DELAY)
        return res
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        time.sleep(REQUEST_DELAY)  # 即使请求失败也等待，避免快速重试
        return None


def bilibili_history(limit=20, page=1, date=today_str) -> List[BilibiliHistoryItem]:
    url = "https://api.bilibili.com/x/v2/history"
    params = {"ps": limit, "pn": page}

    res = make_request('get', url, headers=COMMON_HEADERS, cookies=COOKIES, params=params, name="bilibili_history")
    # 只要当天的视频
    if res and res.status_code == 200:
        return BilibiliHistoryItem.from_json_list(res.json())
    logger.error(f"Failed with status {res.status_code if res else 'N/A'}")
    return []


def get_subtitle_url(aid: int, cid: int) -> Optional[str]:
    url = "https://api.bilibili.com/x/player/wbi/v2"
    params = {
        "aid": aid,
        "cid": cid,
        "isGaiaAvoided": "false"
    }

    # 扩展 COMMON_HEADERS，添加 curl 请求中的额外头字段
    custom_headers = {
        **COMMON_HEADERS,  # 继承原有通用请求头
        "accept": "application/json, text/plain, */*",
        "accept-language": "en,zh;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,ja;q=0.6",
        "dnt": "1",
        "origin": "https://www.bilibili.com",
        "priority": "u=1, i",
        "referer": f"https://www.bilibili.com/video/BV1ZFEaz7EZz/?spm_id_from=333.1391.0.0&vd_source=d9cfa635cfab03be3bb55be9a6a708ef",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }

    res = make_request('get', url, headers=custom_headers, cookies=COOKIES, params=params, name="get_subtitle_url")
    if res and res.status_code == 200 and res.json().get("code") == 0:
        aid = res.json().get("data", {}).get("aid")
        cid = res.json().get("data", {}).get("cid")
        logger.info(f"aid: {aid}")
        logger.info(f"cid: {cid}")
        subtitles = res.json().get("data", {}).get("subtitle", {}).get("subtitles", [])
        return subtitles[0].get("subtitle_url") if subtitles else None
    return None


def get_subtitle_content(subtitle_url: str) -> Optional[str]:
    if subtitle_url.startswith("//"):
        subtitle_url = "https:" + subtitle_url

    res = make_request('get', subtitle_url, headers=COMMON_HEADERS, name="get_subtitle_content")
    if res and res.status_code == 200:
        body = res.json().get("body", [])
        return " ".join([item.get("content", "") for item in body])
    return None
