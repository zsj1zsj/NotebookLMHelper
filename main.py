import sqlite3
import os
import time
import yt_dlp
import ffmpeg
import whisper
import openai
from datetime import datetime


# 初始化SQLite数据库
def init_db():
    conn = sqlite3.connect('youtube_tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS DownloadTasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  youtube_url TEXT,
                  title TEXT,
                  status TEXT,
                  video_path TEXT,
                  audio_path TEXT,
                  srt_path TEXT,
                  summary TEXT,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP)''')
    conn.commit()
    return conn


# 创建下载任务
def create_task(conn, youtube_url):
    c = conn.cursor()
    now = datetime.now()
    c.execute("INSERT INTO DownloadTasks (youtube_url, status, created_at, updated_at) VALUES (?, ?, ?, ?)",
              (youtube_url, 'PENDING', now, now))
    conn.commit()
    return c.lastrowid


# 下载YouTube视频
def download_video(task_id, youtube_url, conn):
    c = conn.cursor()
    c.execute("UPDATE DownloadTasks SET status = ?, updated_at = ? WHERE id = ?",
              ('DOWNLOADING', datetime.now(), task_id))
    conn.commit()

    ydl_opts = {
        'outtmpl': './downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_path = ydl.prepare_filename(info)
            title = info.get('title', 'Unknown Title')
            c.execute("UPDATE DownloadTasks SET status = ?, title = ?, video_path = ?, updated_at = ? WHERE id = ?",
                      ('COMPLETED', title, video_path, datetime.now(), task_id))
            conn.commit()
        return video_path
    except Exception as e:
        c.execute("UPDATE DownloadTasks SET status = ?, updated_at = ? WHERE id = ?",
                  ('FAILED', datetime.now(), task_id))
        conn.commit()
        raise e


# 提取音频
def extract_audio(task_id, video_path, conn):
    audio_path = video_path.replace('.mp4', '.mp3')
    try:
        ffmpeg.input(video_path).output(audio_path, vn=True, acodec='copy').run()
        c = conn.cursor()
        c.execute("UPDATE DownloadTasks SET audio_path = ?, updated_at = ? WHERE id = ?",
                  (audio_path, datetime.now(), task_id))
        conn.commit()
        return audio_path
    except Exception as e:
        c = conn.cursor()
        c.execute("UPDATE DownloadTasks SET status = ?, updated_at = ? WHERE id = ?",
                  ('FAILED', datetime.now(), task_id))
        conn.commit()
        raise e


# 生成字幕
def generate_subtitles(task_id, audio_path, conn):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    srt_content = convert_to_srt(result)  # 假设有此函数将结果转为SRT格式
    srt_path = audio_path.replace('.mp3', '.srt')
    with open(srt_path, 'w') as f:
        f.write(srt_content)
    c = conn.cursor()
    c.execute("UPDATE DownloadTasks SET srt_path = ?, updated_at = ? WHERE id = ?",
              (srt_path, datetime.now(), task_id))
    conn.commit()
    return srt_path, result['text']


# 生成总结
def summarize_content(task_id, text, conn):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Summarize the following video content."},
            {"role": "user", "content": text}
        ]
    )
    summary = response.choices[0].message.content
    c = conn.cursor()
    c.execute("UPDATE DownloadTasks SET summary = ?, status = ?, updated_at = ? WHERE id = ?",
              (summary, 'DONE', datetime.now(), task_id))
    conn.commit()
    return summary


# 转换结果为SRT格式（伪代码）
def convert_to_srt(result):
    srt_lines = []
    for i, segment in enumerate(result['segments']):
        start = segment['start']
        end = segment['end']
        text = segment['text']
        srt_lines.append(f"{i + 1}")
        srt_lines.append(f"{format_time(start)} --> {format_time(end)}")
        srt_lines.append(f"{text}\n")
    return "\n".join(srt_lines)


def format_time(seconds):
    ms = int((seconds % 1) * 1000)
    seconds = int(seconds)
    h, m, s = seconds // 3600, (seconds // 60) % 60, seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# 主任务调度循环
def task_scheduler(conn):
    while True:
        c = conn.cursor()
        c.execute(
            "SELECT id, youtube_url, status, video_path, audio_path, srt_path FROM DownloadTasks WHERE status NOT IN ('FAILED', 'DONE')")
        tasks = c.fetchall()
        for task in tasks:
            task_id, url, status, video_path, audio_path, srt_path = task
            if status == 'PENDING':
                print(f"Starting download for task {task_id}")
                download_video(task_id, url, conn)
            elif status == 'COMPLETED':
                print(f"Extracting audio for task {task_id}")
                extract_audio(task_id, video_path, conn)
            elif status == 'PROCESSING' and audio_path and not srt_path:
                print(f"Generating subtitles for task {task_id}")
                srt_path, text = generate_subtitles(task_id, audio_path, conn)
                summarize_content(task_id, text, conn)
        time.sleep(10)  # 每10秒检查一次


if __name__ == "__main__":
    conn = init_db()
    # 示例：创建任务
    youtube_url = input("请输入YouTube视频链接: ")
    task_id = create_task(conn, youtube_url)
    print(f"任务创建成功，ID: {task_id}")
    # 启动任务调度
    task_scheduler(conn)
