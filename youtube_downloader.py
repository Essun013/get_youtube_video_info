import os
import yt_dlp
from pathlib import Path
from mp4_to_mp3_converter import convert_single_mp4_to_mp3

###########################################################################
# 功能：youtube视频下载工具，输入链接下载视频mp4，自动下载文件名称格式为（视频标题+发布日期）.mp4，放在和该工具同路径的download_mp4文件夹下，然后自动生成对应的mp3文件
# 如果目标文件夹不存在则创建一个文件夹，同时生成一个（视频标题+发布日期）.txt说明文件也放download_mp4文件夹下，
# 说明文件中包含视频的标题，作者，观看次数，发布日期，视频时长，视频描述，MP3下载链接等信息。用python语言实现，用yt-dlp工具包实现。
# python youtube_downloader.py "https://www.youtube.com/watch?v=CkfXR-Fojug" --cookies "C:\Users\linsq\Downloads\www.youtube.com_cookies.txt"
###########################################################################

def ensure_download_dir():
    """确保下载目录存在"""
    download_dir = os.path.join(os.path.dirname(__file__), "download_mp4")
    Path(download_dir).mkdir(exist_ok=True)
    return download_dir

def get_video_info(url, cookies_file=None):
    """获取视频信息"""
    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'noplaylist': True,
            'quiet': True,
            'cookiefile': cookies_file if cookies_file else None,
            'referer': 'https://www.youtube.com/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 检查info是否为None
            if info is None:
                return {"错误": "无法获取视频信息"}
            
            # 获取MP4下载链接
            mp4_url = None
            if 'url' in info:
                mp4_url = info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                mp4_url = info['entries'][0].get('url')
                
            return {
                "视频链接": url,
                "标题": info.get('title', '未知'),
                "作者": info.get('uploader', '未知'),
                "观看次数": info.get('view_count', '未知'),
                "发布日期": info.get('upload_date', '未知'),
                "视频时长": info.get('duration', '未知'),
                "视频描述": info.get('description', '无描述'),
                "MP4下载链接": mp4_url if mp4_url else "无法获取"
            }
    except Exception as e:
        return {"错误": str(e)}

def download_video(url, cookies_file=None):
    """下载视频并生成说明文件"""
    download_dir = ensure_download_dir()
    video_info = get_video_info(url, cookies_file)
    
    if "错误" in video_info:
        print(f"错误: {video_info['错误']}")
        print("提示: 请使用Chrome浏览器登录YouTube账号后，导出cookies.txt文件")
        print("然后使用 --cookies 参数指定cookies文件路径")
        return
    
    # 生成文件名基础
    import re
    filename_base = re.sub(r'[\\/:*?"<>|]', '_', f"{video_info['标题']}_{video_info['发布日期']}")
    
    # 下载视频
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(download_dir, f"{filename_base}.mp4"),
        'quiet': False
    }
    
    if cookies_file:
        ydl_opts['cookiefile'] = cookies_file
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"视频已下载到: {ydl_opts['outtmpl']}")
        
        # 转换为MP3
        mp4_path = os.path.join(download_dir, f"{filename_base}.mp4")
        mp3_path = convert_single_mp4_to_mp3(mp4_path)
        if mp3_path:
            print(f"MP3已生成: {mp3_path}")
        else:
            print("MP3转换失败")
            
    except Exception as e:
        print(f"视频下载失败: {str(e)}")
        if "ffmpeg" in str(e).lower():
            print("提示: 需要安装ffmpeg以支持高质量视频下载")
            print("安装方法: https://ffmpeg.org/download.html")
        return
    
    # 生成说明文件
    info_file = os.path.join(download_dir, f"{filename_base}.txt")
    with open(info_file, 'w', encoding='utf-8') as f:
        for key, value in video_info.items():
            f.write(f"{key}: {value}\n")
    print(f"视频信息已保存到: {info_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube视频下载工具')
    parser.add_argument('url', help='YouTube视频链接')
    parser.add_argument('--cookies', help='cookies文件路径', required=False)
    
    args = parser.parse_args()
    
    download_video(args.url, args.cookies)