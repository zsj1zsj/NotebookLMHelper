import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
AUDIOBOOKSHELF_TOKEN = os.environ.get("AUDIOBOOKSHELF_TOKEN", "")

# Audiobookshelf 服务器地址和 API 密钥
SERVER_URL = "http://192.168.1.13:7331"
API_TOKEN = AUDIOBOOKSHELF_TOKEN

# 设置请求头，包含 API 密钥
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}


def get_recently_played():
    """
    通过 Audiobookshelf API 获取最近听过的音频
    """
    try:
        # 构造 API 端点 URL
        endpoint = f"{SERVER_URL}/api/me/listening-stats"

        # 发送 GET 请求获取收听统计数据
        response = requests.get(endpoint, headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            data = response.json()

            # 提取 recentSessions 部分
            recent_sessions = data.get('recentSessions', [])

            if recent_sessions:
                print("最近听过的音频:")
                for index, session in enumerate(recent_sessions, 1):
                    library_item_id = session.get('libraryItemId', '未知')
                    display_title = session.get('displayTitle', '未知标题')
                    display_author = session.get('displayAuthor', '未知作者')
                    time_listening = session.get('timeListening', 0)
                    session_date = session.get('date', '未知日期')
                    updated_at = session.get('updatedAt', 0)

                    # 将时间戳转换为可读格式
                    updated_at_dt = datetime.fromtimestamp(updated_at / 1000).strftime(
                        '%Y-%m-%d %H:%M:%S') if updated_at else '未知时间'

                    print(f"{index}. 标题: {display_title}")
                    print(f"   作者: {display_author}")
                    print(f"   音频 ID: {library_item_id}")
                    print(f"   收听时间: {time_listening} 秒")
                    print(f"   日期: {session_date}")
                    print(f"   最后更新: {updated_at_dt}")
                    print("")
            else:
                print("没有找到最近听过的音频记录。")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"发生错误: {e}")


# 执行函数
if __name__ == "__main__":
    get_recently_played()
