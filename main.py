from api import bilibili_history, get_subtitle_url, get_subtitle_content
from logger_setup import logger

if __name__ == "__main__":
    history = bilibili_history()
    for i, item in enumerate(history, 1):
        logger.info(f"Item {i}:\n{item}")

    if history:
        aid, cid = history[0].aid, history[0].cid
        subtitle_url = get_subtitle_url(aid, cid)
        if subtitle_url:
            logger.info(f"Subtitle URL: {subtitle_url}")
            content = get_subtitle_content(subtitle_url)
            logger.info(f"Subtitle Content: {content}")
        else:
            logger.warning("No subtitle found.")
