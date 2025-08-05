from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)


## 访问 http://127.0.0.1:8000/?url=https://www.youtube.com/watch?v=zDPE5citB9Q
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
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
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
            "msg": str(e),
            "src_url": url
        }), 500

if __name__ == '__main__':
    app.run(port=8000)

# 示例代码：使用 yt-dlp 获取视频信息
import subprocess

command = ['yt-dlp', '--cookies-from-browser', 'chrome', 'https://youtu.be/zDPE5citB9Q']
result = subprocess.run(command, capture_output=True, text=True)
print(result.stdout)