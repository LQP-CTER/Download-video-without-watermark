# Rita - Telegram Bot for Analysis and Download

## 📌 Overview
Rita is a Telegram bot that allows users to analyze and download videos and images without watermarks. It fetches metadata, including view count, likes, comments, and shares, while also providing high-quality download links.

## 🚀 Features
- **Analyze TikTok videos**: Get metadata like title, author, hashtags, and engagement metrics.
- **Download TikTok videos/images**: Save TikTok videos and images without watermarks.
- **Shortened HD video links**: Generate shortened links for easy sharing.
- **User activity logging**: Stores user interaction data for future enhancements.

## 🛠️ Setup
### Prerequisites
- Python 3.8+
- Required dependencies

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/lqp-cter/rita-telegram-bot.git
   cd rita-telegram-bot
   ```
2. Install required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up your Telegram bot:
   - Obtain an API key from [BotFather](https://t.me/BotFather) on Telegram.
   - Replace `API_KEY` in the script with your bot token.
4. Run the bot:
   ```sh
   python main.py
   ```

## 🔧 Configuration
### Environment Variables
- `API_KEY`: Your Telegram bot API token.
- `X-RapidAPI-Key`: Your RapidAPI key for TikTok data fetching.
- `DOWNLOAD_FOLDER`: Directory to store downloaded media files.

## 📜 Usage
### Start the Bot
To start interacting with Rita, send the `/start` command.

### Analyze TikTok Video
Use the command:
```sh
/analysis <TikTok Video URL>
```
The bot will fetch metadata like title, author, hashtags, views, likes, and comments.

### Download TikTok Video/Image
Use the command:
```sh
/video <TikTok Video URL>
```
Rita will process and send the media file directly in the chat.

## 📂 File Structure
```
├── Downloads/            # Directory for downloaded media
├── main.py               # Main bot script
├── requirements.txt      # Dependencies
├── user_data.txt         # User activity log
├── README.md             # Documentation
```

## 📌 Dependencies
- `python-telegram-bot`
- `requests`
- `pandas`
- `pyshorteners`
- `hashlib`

Install them via:
```sh
pip install -r requirements.txt
```

## 💡 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.

## 🛡️ License
This project is open-source and licensed under the MIT License.

## 📬 Contact
For issues or feature requests, contact [Lê Qúy Phát](https://t.me/CterLQP).

---
Thank you for using Rita! 😊

