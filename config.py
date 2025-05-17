import os
from dotenv import load_dotenv

load_dotenv()
BILIBILI_SESSDATA = os.environ.get("BILIBILI_SESSDATA", "")

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

COOKIES = {
    "SESSDATA": BILIBILI_SESSDATA
}
