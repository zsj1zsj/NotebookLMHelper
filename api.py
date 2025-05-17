import requests
from typing import Optional, List
from logger_setup import logger
from config import COMMON_HEADERS, COOKIES
from bilibili_models import BilibiliHistoryItem


def _log_response(name: str, response: requests.Response):
    logger.info(f"{name} Status Code: {response.status_code}")
    logger.debug(f"{name} Headers: {response.request.headers}")
    logger.debug(f"{name} Body: {response.text[:500]}...")


def bilibili_history(limit=10, page=1) -> List[BilibiliHistoryItem]:
    url = "https://api.bilibili.com/x/v2/history"
    params = {"ps": limit, "pn": page}

    try:
        res = requests.get(url, headers=COMMON_HEADERS, cookies=COOKIES, params=params)
        _log_response("bilibili_history", res)
        if res.status_code == 200:
            return BilibiliHistoryItem.from_json_list(res.json())
        logger.error(f"Failed with status {res.status_code}")
    except Exception as e:
        logger.error(f"Error in bilibili_history: {e}")
    return []


def get_subtitle_url(aid: int, cid: int) -> Optional[str]:
    url = "https://api.bilibili.com/x/player/v2"
    params = {"aid": aid, "cid": cid}

    try:
        res = requests.get(url, headers=COMMON_HEADERS, cookies=COOKIES, params=params)
        _log_response("get_subtitle_url", res)
        if res.status_code == 200 and res.json().get("code") == 0:
            subtitles = res.json().get("data", {}).get("subtitle", {}).get("subtitles", [])
            return subtitles[0].get("subtitle_url") if subtitles else None
    except Exception as e:
        logger.error(f"Error in get_subtitle_url: {e}")
    return None


def get_subtitle_content(subtitle_url: str) -> Optional[str]:
    if subtitle_url.startswith("//"):
        subtitle_url = "https:" + subtitle_url
    try:
        res = requests.get(subtitle_url, headers=COMMON_HEADERS)
        _log_response("get_subtitle_content", res)
        if res.status_code == 200:
            body = res.json().get("body", [])
            return " ".join([item.get("content", "") for item in body])
    except Exception as e:
        logger.error(f"Error in get_subtitle_content: {e}")
    return None
