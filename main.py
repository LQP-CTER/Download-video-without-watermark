import os
import re
import requests
import time
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from pyshorteners import Shortener
import hashlib

# API Key của bạn từ Telegram
API_KEY = '***************************'
DOWNLOAD_FOLDER = './Downloads'
LOG_FILE = 'user_activity_log.txt'

# Function to log user activity
def save_data_user(update, context):
    log_file_path = 'user_data.txt'

    chat_id = update.effective_chat.id
    username = update.effective_user.username or "UnknownUser"
    first_name = update.effective_user.first_name or ""
    last_name = update.effective_user.last_name or ""
    message_text = update.message.text
    timestamp = update.message.date.strftime('%Y-%m-%d %H:%M:%S')

    new_data = pd.DataFrame({
        "Timestamp": [timestamp],
        "Chat ID": [chat_id],
        "Username": [username],
        "Full Name": [f"{first_name} {last_name}"],
        "Message": [message_text]
    })

    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 0:
        existing_data = pd.read_csv(log_file_path, sep='\t', quotechar='"', escapechar='\\')
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        updated_data = new_data

    updated_data.to_csv(log_file_path, index=False, sep='\t', quotechar='"', escapechar='\\')

# Function to sanitize filename
def sanitize_filename(filename, max_length=100):
    sanitized_filename = re.sub(r'[<>:"/\\|?*#]', '_', filename)
    if len(sanitized_filename) > max_length:
        root, ext = os.path.splitext(sanitized_filename)
        sanitized_filename = root[:max_length - len(ext)] + ext
    return sanitized_filename

# Function to create a hash-based filename
def hash_filename(filename, max_length=100):
    file_hash = hashlib.sha256(filename.encode()).hexdigest()
    root, ext = os.path.splitext(filename)
    hashed_filename = f"{root[:max_length-len(ext)]}_{file_hash[:8]}{ext}"
    return hashed_filename

# Analyze video TikTok
async def analyze_tiktok(update: Update, context: CallbackContext):
    try:
        video_url = context.args[0]
        api_url = "https://tiktok-scraper7.p.rapidapi.com/"
        querystring = {"url": video_url}
        headers = {
            "X-RapidAPI-Key": "********************************",
            "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com"
        }

        response = requests.get(api_url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        if data['code'] == 0:
            video_data = data['data']
            title = video_data.get('title', "Không có tiêu đề")
            author_nickname = video_data['author']['nickname']
            music_title = video_data['music_info'].get('title', "Không có nhạc nền")
            hashtags = [f"#{tag}" for tag in video_data['title'].split() if tag.startswith('#')]
            view_count = video_data.get('play_count', 0)
            like_count = video_data.get('digg_count', 0)
            comment_count = video_data.get('comment_count', 0)
            share_count = video_data.get('share_count', 0)
            download_count = video_data.get('download_count', 0)
            duration = video_data.get('duration', 0)
            create_time = video_data.get('create_time', 0)
            region = video_data.get('region', "Không rõ")

            video_url_hd = video_data.get('hdplay', video_data.get('play', None))
            try:
                shortener = Shortener()
                video_url_hd = shortener.tinyurl.short(video_url_hd)
            except requests.RequestException:
                pass

            response_message = f"""
                🎬 Tiêu đề: {title}
                👤 Tác giả: {author_nickname}
                🎵 Nhạc nền: {music_title}
                # Hashtags: {' '.join(hashtags)}
                👁️ Lượt xem: {view_count}
                👍 Lượt thích: {like_count}
                💬 Bình luận: {comment_count}
                🔁 Chia sẻ: {share_count}
                ⬇️ Tải xuống: {download_count}
                ⏱️ Thời lượng: {duration} giây
                📅 Ngày đăng: {time.strftime('%Y-%m-%d', time.localtime(create_time))}
                🌎 Khu vực: {region}
            """
            if video_url_hd:
                response_message += f"\n🔗 Link HD: {video_url_hd}"

            await update.message.reply_text(response_message)
        else:
            await update.message.reply_text("Lỗi: Không thể lấy thông tin video.")

        save_data_user(update, context)

    except requests.RequestException as e:
        await update.message.reply_text(f"Lỗi mạng: {e}")
    except Exception as e:
        await update.message.reply_text(f"Lỗi: {e}")

# Download TikTok media
def download_tiktok_media(video_url, download_folder="Downloads"):
    api_url = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"
    payload = {"url": video_url}
    headers = {
        "x-rapidapi-key": "dc65a367e9mshbf934df4bee4484p18e20bjsn77d89d04446d",
        "x-rapidapi-host": "auto-download-all-in-one.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        # Ensure the download folder exists
        os.makedirs(download_folder, exist_ok=True)

        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'medias' not in data or not data['medias']:
            raise ValueError("API không trả về phương tiện nào")

        media_files = []

        for media in data['medias']:
            media_url = media['url']
            media_type = media['type']
            media_extension = media.get('extension', 'unknown')

            # Sanitize filename
            if media_type == 'video' and media['quality'] == 'hd_no_watermark':
                video_title = sanitize_filename(hash_filename(data.get('title', 'tiktok_video')))
                file_path = os.path.join(download_folder, f"{video_title}.mp4")
                media_files.append(file_path)

                with requests.get(media_url, stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

            elif media_type == 'image':
                image_title = sanitize_filename(hash_filename(data.get('title', 'tiktok_image')))
                file_path = os.path.join(download_folder, f"{image_title}.{media_extension}")
                media_files.append(file_path)

                with requests.get(media_url, stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

        return media_files

    except requests.RequestException as e:
        raise Exception(f"Lỗi mạng: {e}")

    except Exception as e:
        raise Exception(f"Lỗi: {e}")


# Command download video hoặc hình ảnh TikTok
async def tiktok_dl(update: Update, context: CallbackContext) -> None:
    args = context.args
    if not args:
        await update.message.reply_text("Vui lòng cung cấp URL video hoặc ảnh TikTok sau lệnh /video")
        return

    video_url = args[0]
    try:
        media_files = download_tiktok_media(video_url)

        for file_path in media_files:
            if file_path.endswith('.mp4'):
                with open(file_path, 'rb') as f:
                    await context.bot.send_video(chat_id=update.effective_chat.id, video=f)
            else:
                with open(file_path, 'rb') as f:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)

            os.remove(file_path)

        save_data_user(update, context)

    except Exception as e:
        await update.message.reply_text(f"Lỗi: {e}")

# Function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    welcome_message = (
        "🎉 *Xin chào!* 🎉\n\n"
        "Đây là *Rita*, bot hỗ trợ phân tích và tải video TikTok.\n\n"
        "Bạn có thể sử dụng các lệnh sau để tương tác với bot:\n\n"
        "🔍 */analysis <url>*\n"
        "Phân tích video TikTok.\n\n"
        "📥 */video <url>*\n"
        "Tải video hoặc hình ảnh TikTok không có watermark.\n\n"
        "Nếu bot ngừng hoạt động, hãy thông báo đến tôi:\n"
        "👉 [Lê Qúy Phát](https://t.me/CterLQP)\n\n"
        "Ngoài ra, nếu bạn muốn trải nghiệm các mô hình AI hoạt động như ChatGPT hay Gemini,"
        "hãy thử sử dụng [Rita AI](https://t.me/AI_Rita_bot)\n\n"
        "Mình vẫn sẽ phát triển thêm các tool bot này, nên xin mọi người đừng ngần ngại góp ý thêm cho mình nhé. "
        "Cảm ơn bạn đã sử dụng Rita! 😊 \n"
    )

    save_data_user(update, context)
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# Hàm main để chạy bot
def main():
    application = Application.builder().token(API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analysis", analyze_tiktok))
    application.add_handler(CommandHandler("video", tiktok_dl))

    application.run_polling()

if __name__ == "__main__":
    main()
