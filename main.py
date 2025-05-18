from api import bilibili_history, get_subtitle_url, get_subtitle_content
from logger_setup import logger
from datetime import datetime

def get_today_date():
    """
    获取今天的日期，返回格式为 YYYYMMDD 的字符串。

    返回:
        str: 今天的日期字符串，格式为 YYYYMMDD
    """
    today = datetime.today()
    return today.strftime("%Y%m%d")


def write_to_file(title, content, directory=f'/Users/lynn/Documents/notebooklm/{get_today_date()}'):
    """
    将内容写入以 title 为文件名的文本文件，文件存放在指定目录中。
    如果文件已存在，则忽略不写入。

    参数:
        title (str): 文件名（不包含后缀）
        content (str): 要写入文件的内容
        directory (str): 文件存放的目录路径
    """
    try:
        # 构造完整文件路径，添加 .txt 后缀
        import os
        # 确保目录存在，如果不存在则创建
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = os.path.join(directory, f"{title}.txt")
        # 检查文件是否存在
        if os.path.exists(filename):
            print(f"文件已存在，忽略写入: {filename}")
            return
        # 以写入模式打开文件（文件不存在时会自动创建）
        with open(filename, 'w', encoding='utf-8') as file:
            # 写入内容
            file.write(content)
        print(f"成功写入文件: {filename}")
    except Exception as e:
        print(f"写入文件时出错: {e}")


# 示例用法
if __name__ == "__main__":
    title = "example"
    content = "这是一个测试内容。\n换行内容。"
    directory = "output_folder"
    write_to_file(title, content, directory)

if __name__ == "__main__":
    history = bilibili_history()
    for i, item in enumerate(history, 0):
        logger.info(f'-----{i}   EBEGIN--------')
        logger.info(f"Item {i}:\n{item}")
        aid, cid = item.aid, item.cid
        subtitle_url = get_subtitle_url(aid, cid)
        if subtitle_url:
            logger.info(f"Subtitle URL: {subtitle_url}")
            content = get_subtitle_content(subtitle_url)
            logger.info(item.title)
            logger.info(f"Subtitle Content: {content}")
            write_to_file(item.title, content)
        else:
            logger.warning("No subtitle found.")
        logger.info(f'-----{i}   END--------')
