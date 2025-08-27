from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)


## 访问 http://127.0.0.1:8000/?url=https://www.youtube.com/watch?v=zDPE5citB9Q
## http://127.0.0.1:8000/?url=https://www.youtube.com/watch?v=6GBfKCCYcR4&cookies_file=<Cookie文件路径>
@app.route('/')
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({
            "code": "error",
            "msg": "Missing url parameter",
            "src_url": ""
        }), 400
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'noplaylist': True,
            # 支持手动传入 Cookie 文件路径
            'cookiefile': request.args.get('cookies_file') or None
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 检查 info 是否为有效的字典类型
            if not info or not isinstance(info, dict):
                return jsonify({
                    "code": "error",
                    "data": {},
                    "msg": "Failed to extract video information",
                    "src_url": url
                }), 500
            
            mp3_url = None
            if 'url' in info:
                mp3_url = info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                mp3_url = info['entries'][0].get('url')
                
            video_info = {
                "title": info.get('title', 'unknown'),
                "author": info.get('uploader', 'unknown'),
                "views": info.get('view_count', 'unknown'),
                "publish_date": info.get('upload_date', 'unknown'),
                "duration": info.get('duration', 'unknown'),
                "description": info.get('description', 'no description'),
                "mp3_url": mp3_url if mp3_url else "unavailable"
            }
            
            return jsonify({
                "code": "success",
                "data": video_info,
                "msg": "",
                "src_url": url
            })
            
    except Exception as e:
        return jsonify({
            "code": "error",
            "data": {},
            "msg": "Failed to fetch video info. If YouTube requires login, provide a cookies file via 'cookies_file' parameter. See https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp",
            "src_url": url
        }), 500

if __name__ == '__main__':
    app.run(port=8000)