import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv


# 设置日志配置
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
    handlers=[
        logging.StreamHandler()  # 输出到控制台
        # 可以添加 logging.FileHandler('app.log') 将日志写入文件
    ]
)

# 创建 logger 对象
logger = logging.getLogger(__name__)

load_dotenv()
BILIBILI_SESSDATA = os.environ.get("BILIBILI_SESSDATA", "")
print("env:" + BILIBILI_SESSDATA)

# 定义 BilibiliHistoryItem 类，新增 aid 和 cid 字段
class BilibiliHistoryItem:
    def __init__(self, title: str, redirect_link: str, short_link: str, bvid: str,
                 aid: int, cid: int, pubdate: int, duration: int, view_at: int,
                 owner_name: str, view_count: int, like_count: int, favorite_count: int,
                 coin_count: int, share_count: int):
        """
        初始化 Bilibili 历史记录项

        参数:
            title: 视频标题
            redirect_link: 视频完整链接
            short_link: 视频短链接
            bvid: 视频 BVID
            aid: 视频 AV 号
            cid: 视频 CID（分P标识）
            pubdate: 视频发布时间（Unix 时间戳）
            duration: 视频时长（秒）
            view_at: 用户观看时间（Unix 时间戳）
            owner_name: 视频作者名称
            view_count: 播放量
            like_count: 点赞数
            favorite_count: 收藏数
            coin_count: 投币数
            share_count: 分享数
        """
        self.title = title
        self.redirect_link = redirect_link
        self.short_link = short_link
        self.bvid = bvid
        self.aid = aid
        self.cid = cid
        self.pubdate = pubdate
        self.pubdate_str = datetime.fromtimestamp(pubdate).strftime('%Y-%m-%d %H:%M:%S')
        self.duration = duration
        self.view_at = view_at
        self.view_at_str = datetime.fromtimestamp(view_at).strftime('%Y-%m-%d %H:%M:%S')
        self.owner_name = owner_name
        self.view_count = view_count
        self.like_count = like_count
        self.favorite_count = favorite_count
        self.coin_count = coin_count
        self.share_count = share_count

    def __str__(self) -> str:
        """返回格式化的字符串表示"""
        return (f"Title: {self.title}\n"
                f"Owner: {self.owner_name}\n"
                f"URL: {self.redirect_link}\n"
                f"Short URL: {self.short_link}\n"
                f"BVID: {self.bvid}, AID: {self.aid}, CID: {self.cid}\n"
                f"Published: {self.pubdate_str}\n"
                f"Viewed At: {self.view_at_str}\n"
                f"Duration: {self.duration}s\n"
                f"Views: {self.view_count}, Likes: {self.like_count}, "
                f"Favorites: {self.favorite_count}, Coins: {self.coin_count}, "
                f"Shares: {self.share_count}\n")

    @classmethod
    def from_json(cls, json_data: Dict) -> 'BilibiliHistoryItem':
        """从 JSON 数据创建单个历史记录项"""
        return cls(
            title=json_data.get('title', ''),
            redirect_link=json_data.get('redirect_link', ''),
            short_link=json_data.get('short_link_v2', ''),
            bvid=json_data.get('bvid', ''),
            aid=json_data.get('aid', 0),
            cid=json_data.get('cid', 0),
            pubdate=json_data.get('pubdate', 0),
            duration=json_data.get('duration', 0),
            view_at=json_data.get('view_at', 0),
            owner_name=json_data.get('owner', {}).get('name', ''),
            view_count=json_data.get('stat', {}).get('view', 0),
            like_count=json_data.get('stat', {}).get('like', 0),
            favorite_count=json_data.get('stat', {}).get('favorite', 0),
            coin_count=json_data.get('stat', {}).get('coin', 0),
            share_count=json_data.get('stat', {}).get('share', 0)
        )

    @classmethod
    def from_json_list(cls, json_response: Dict) -> List['BilibiliHistoryItem']:
        """从 API 响应 JSON 创建历史记录项列表"""
        data_list = json_response.get('data', [])
        return [cls.from_json(item) for item in data_list]


# bilibili_history 函数保持不变
def bilibili_history() -> List[BilibiliHistoryItem]:
    """
    获取 Bilibili 历史记录数据，并返回 BilibiliHistoryItem 对象列表

    返回值:
        List[BilibiliHistoryItem]: 包含历史记录项的列表
    """
    # 构建请求 URL 和参数
    url = "https://api.bilibili.com/x/v2/history"
    params = {
        "ps": 10,
        "pn": 1
    }

    # 设置 Cookie
    cookies = {
        "SESSDATA": BILIBILI_SESSDATA
    }

    # 设置自定义请求头，模拟浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    try:
        # 发送 GET 请求
        response = requests.get(url, params=params, cookies=cookies, headers=headers)

        # 使用 logger 记录日志信息
        logger.info(f"Status Code: {response.status_code}")
        logger.debug(f"Request Headers: {response.request.headers}")
        logger.debug(f"Response Text: {response.text[:500]}...' if len(response.text) > 500 else {response.text}")

        # 检查响应状态码是否为 200
        if response.status_code == 200:
            # 解析 JSON 响应
            json_response = response.json()
            # 返回 BilibiliHistoryItem 对象列表
            return BilibiliHistoryItem.from_json_list(json_response)
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            return []

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return []


def get_subtitle_url(aid: int, cid: int) -> Optional[str]:
    """
    从 Bilibili 播放器 API 获取指定视频的字幕 URL

    参数:
        aid: 视频 AV 号
        cid: 视频 CID（分P标识）

    返回值:
        Optional[str]: 字幕 URL，如果获取失败或无字幕则返回 None
    """
    # 构建请求 URL 和参数
    url = "https://api.bilibili.com/x/player/v2"
    params = {
        "aid": aid,
        "cid": cid
    }
    # 设置 Cookie (使用你提供的 SESSDATA，必要时替换为有效 Cookie)
    cookies = {
        "SESSDATA": BILIBILI_SESSDATA
    }
    # 设置自定义请求头，模拟浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }
    try:
        # 发送 GET 请求
        response = requests.get(url, params=params, cookies=cookies, headers=headers)
        # 使用 logger 记录日志信息
        logger.info(f"get_subtitle_url Status Code: {response.status_code}")
        logger.debug(f"get_subtitle_url Request Headers: {response.request.headers}")
        logger.debug(f"get_subtitle_url Response Text: {response.text[:500]}...' if len(response.text) > 500 else {response.text}")
        # 检查响应状态码是否为 200
        if response.status_code == 200:
            # 解析 JSON 响应
            json_response = response.json()
            # 检查响应代码是否为 0（表示成功）
            if json_response.get("code") == 0:
                # 获取字幕列表
                subtitle_data = json_response.get("data", {}).get("subtitle", {}).get("subtitles", [])

                # 如果有字幕数据，取第一个字幕的 URL
                if subtitle_data:
                    subtitle_url = subtitle_data[0].get("subtitle_url", "")
                    if subtitle_url:
                        return subtitle_url
                    else:
                        logger.warning("No subtitle URL found in the first subtitle entry.")
                        return None
                else:
                    logger.warning("No subtitles available for this video.")
                    return None
            else:
                logger.error(f"API request failed with code: {json_response.get('code')} and message: {json_response.get('message')}")
                return None
        else:
            logger.error(f"HTTP request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"An error occurred in get_subtitle_url: {str(e)}")
        return None


def get_subtitle_content(subtitle_url: str) -> Optional[str]:
    """
    从 Bilibili 字幕 URL 获取字幕内容，并合并成一个字符串

    参数:
        subtitle_url: 字幕文件的 URL（可能以 // 开头，需要添加 https:）

    返回值:
        Optional[str]: 合并后的字幕内容字符串，如果获取失败则返回 None
    """
    # 如果 URL 以 // 开头，补充 https: 前缀
    if subtitle_url.startswith("//"):
        subtitle_url = "https:" + subtitle_url
    # 设置自定义请求头，模拟浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }
    try:
        # 发送 GET 请求
        response = requests.get(subtitle_url, headers=headers)
        # 使用 logger 记录日志信息
        logger.info(f"get_subtitle_content Status Code: {response.status_code}")
        logger.debug(f"get_subtitle_content Request Headers: {response.request.headers}")
        logger.debug(f"get_subtitle_content Response Text: {response.text[:500]}...' if len(response.text) > 500 else {response.text}")
        # 检查响应状态码是否为 200
        if response.status_code == 200:
            # 解析 JSON 响应
            json_response = response.json()
            # 获取字幕内容列表 (body 数组)
            body_data = json_response.get("body", [])

            # 提取所有 content 字段并合并成一个字符串
            if body_data:
                content_list = [item.get("content", "") for item in body_data]
                merged_content = " ".join(content_list)  # 用空格分隔每段内容
                return merged_content
            else:
                logger.warning("No subtitle content found in the response.")
                return None
        else:
            logger.error(f"HTTP request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"An error occurred in get_subtitle_content: {str(e)}")
        return None


# 示例使用
if __name__ == "__main__":
    # 获取历史记录数据
    history_items = bilibili_history()

    # 使用 logger 打印历史记录项
    if history_items:
        for index, item in enumerate(history_items, 1):
            logger.info(f"Item {index}:")
            logger.info(str(item))
    else:
        logger.warning("No history items retrieved.")

    # 获取字幕 URL 并打印
    sub_url = "http:" + get_subtitle_url(1252861133, 1500609314) if get_subtitle_url(1252861133, 1500609314) else ""
    logger.info(f"Subtitle URL: {sub_url}")

    # 获取字幕内容并打印
    if sub_url:
        subtitle = get_subtitle_content(sub_url)
        if subtitle:
            logger.info(f"Subtitle Content:\n{subtitle}")
        else:
            logger.warning("Failed to retrieve subtitle content.")
    else:
        logger.warning("Failed to retrieve subtitle URL.")
