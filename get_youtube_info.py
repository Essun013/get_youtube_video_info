import yt_dlp

def get_youtube_video_info(url):
    """
    获取YouTube视频的基本信息
    :param url: YouTube视频链接
    :return: 包含视频标题、作者、观看次数、发布日期等信息的字典
    """
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 获取MP3下载链接
            mp3_url = None
            if 'url' in info:
                mp3_url = info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                mp3_url = info['entries'][0].get('url')
                
            video_info = {
                "标题": info.get('title', '未知'),
                "作者": info.get('uploader', '未知'),
                "观看次数": info.get('view_count', '未知'),
                "发布日期": info.get('upload_date', '未知'),
                "视频时长": info.get('duration', '未知'),
                "视频描述": info.get('description', '无描述'),
                "MP3下载链接": mp3_url if mp3_url else "无法获取"
            }
        return video_info
    except Exception as e:
        return {"错误": str(e)}

if __name__ == "__main__":
    video_url = input("请输入YouTube视频链接: ")
    info = get_youtube_video_info(video_url)
    for key, value in info.items():
        print(f"{key}: {value}")