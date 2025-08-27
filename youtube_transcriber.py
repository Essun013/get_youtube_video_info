import os
import requests
import uuid
import time, random
import yt_dlp
from pathlib import Path
from urllib.parse import urljoin

# 功能：输入youtube视频链接，直接生成文本文件！
# 执行方法：python youtube_transcriber.py "https://www.youtube.com/watch?v=dFZIe6H67Vo"
# 依赖：pip install yt-dlp
# 依赖：pip install requests

# 配置参数
cookies_file = "C:\\Users\\linsq\\Downloads\\www.youtube.com_cookies.txt"
API_KEY = "sk-24fb02c39f784ff888b7a3b3db5ed6e6"
API_TRANS_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
API_TASK_STATUS_URL = "https://dashscope.aliyuncs.com/api/v1/tasks"
PUBLIC_MP3_URL = "https://www.dfs521.com/mp3/"
MODEL = "paraformer-v2"

def ensure_download_dir():
    """确保下载目录存在"""
    download_dir = os.path.join(os.path.dirname(__file__), "download_mp4")
    Path(download_dir).mkdir(exist_ok=True)
    return download_dir

def convert_mp4_to_mp3(mp4_path):
    """将MP4转换为MP3"""
    mp3_path = os.path.splitext(mp4_path)[0] + ".mp3"
    if os.path.exists(mp3_path):
        return mp3_path
    
    try:
        # 使用ffmpeg转换
        import subprocess
        subprocess.run([
            "ffmpeg", "-i", mp4_path,
            "-vn", "-acodec", "libmp3lame",
            "-ab", "192k", "-ar", "44100",
            mp3_path
        ], check=True)
        return mp3_path
    except Exception as e:
        print(f"MP4转MP3失败: {str(e)}")
        return None

def upload_mp3(mp3_path):
    """上传MP3文件到公网地址"""
    max_retries = 3
    retry_delay = 5  # 秒
    session = None  # 初始化 session 变量
    
    for attempt in range(max_retries):
        try:
            filename = f"{uuid.uuid4().hex}.mp3"
            upload_url = urljoin(PUBLIC_MP3_URL, filename)
            
            # 每次上传创建独立的会话
            session = requests.Session()
            session.verify = False  # 禁用SSL验证（临时方案）
            
            with open(mp3_path, "rb") as f:
                response = session.put(upload_url, data=f, timeout=30)
                if response.status_code not in [201, 204]:
                    raise Exception(f"文件上传失败: {response.text}")
                
                print(f"MP3文件已上传到: {upload_url}")
                
                # 验证文件可访问性
                for _ in range(max_retries):
                    try:
                        head_resp = session.head(upload_url, timeout=10)
                        if head_resp.status_code == 200:
                            print(f"文件已确认可访问: {upload_url}")
                            return upload_url
                        time.sleep(retry_delay)
                    except Exception as e:
                        print(f"验证失败: {str(e)}")
                        time.sleep(retry_delay)
                
                raise Exception("文件未就绪: 超过最大重试次数")
                
        except Exception as e:
            print(f"上传失败（尝试 {attempt + 1}/{max_retries}）: {str(e)}")
            if attempt == max_retries - 1:
                raise Exception(f"上传MP3文件失败: {str(e)}")
            time.sleep(retry_delay)
            
        finally:
            if session is not None:
                session.close()  # 确保会话关闭

def recognize_speech(mp3_url):
    """调用语音识别API"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    
    payload = {
        "model": MODEL,
        "input": {"file_urls": [mp3_url]},
        "parameters": {"enable_timestamp": False}
    }
    
    # 打印调试信息
    print(f"正在调用阿里百炼API，URL: {mp3_url}，录音文件识别大模型：{MODEL}")
    try:
        response = requests.post(API_TRANS_URL, headers=headers, json=payload, timeout=50)
        
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                task_status = result["output"]["task_status"]
                
                # 轮询任务状态
                max_retries = 50
                for _ in range(max_retries):
                    # 20~30秒随机生成
                    retry_interval = random.randint(20, 30)
                    if task_status == "SUCCEEDED":
                        task_result = requests.post(
                            f"{API_TASK_STATUS_URL}/{task_id}",
                            headers=headers,
                            timeout=60
                        ).json()
                        print(f"taskId（{task_id}）第{_+1}次尝试, 任务状态: {task_status}, 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}, 转换成功！")
                        
                        if "output" in task_result and "results" in task_result["output"]:
                            transcription_url = task_result["output"]["results"][0]["transcription_url"]
                            transcription_response = requests.get(transcription_url, timeout=60)
                            if transcription_response.status_code == 200:
                                transcription_data = transcription_response.json()
                                if "transcripts" in transcription_data and len(transcription_data["transcripts"]) > 0:
                                    print(f"{mp3_url}转换后的文本：")
                                    print(f"{transcription_data["transcripts"][0]["text"]}")
                                    return transcription_data["transcripts"][0]["text"]
                                else:
                                    raise Exception("无效的转录数据格式")
                            else:
                                raise Exception("获取转录数据失败")
                        else:
                            raise Exception("任务结果格式异常")
                        
                    elif task_status in ["RUNNING", "PENDING"]:
                        print(f"taskId（{task_id}）第{_+1}次尝试, 任务状态: {task_status}, 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}, 等待 {retry_interval} 秒后重试...")
                        time.sleep(retry_interval)
                        task_status = requests.post(
                            f"{API_TASK_STATUS_URL}/{task_id}",
                            headers=headers,
                            timeout=60
                        ).json().get("output", {}).get("task_status", "PENDING")
                    
                    elif task_status == "FAILED":
                        raise Exception("语音识别任务失败")
                
                raise Exception("语音识别任务未完成: 超过最大轮询次数")
            else:
                raise Exception("API响应格式异常")
        else:
            raise Exception(f"语音识别失败: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API请求异常: {str(e)}")

def download_and_transcribe(url, cookies_file=None):
    """主流程: 下载视频并转文本"""
    try:
        # 1. 下载视频
        download_dir = ensure_download_dir()
        mp4_format = 'worst[ext=mp4]' # 选择最低清晰度的MP4格式  高清晰度设置为：'best[ext=mp4]/best'
        ydl_opts = {
            'format': mp4_format,
            'noplaylist': True,
            'quiet': True,
            'cookiefile': cookies_file if cookies_file else None,
            'referer': 'https://www.youtube.com/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        mp4_url, mp4_path = None, None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # 检查 info 是否为 None
            if info is None:
                raise Exception("无法获取视频信息")
            
            # 获取MP4下载链接
            if 'url' in info:
                mp4_url = info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                mp4_url = info['entries'][0].get('url')
                
            video_info = {
                "视频链接": url,
                "标题": info.get('title', '未知'),
                "作者": info.get('uploader', '未知'),
                "观看次数": info.get('view_count', '未知'),
                "发布日期": info.get('upload_date', '未知'),
                "视频时长": info.get('duration', '未知'),
                "视频描述": info.get('description', '无描述'),
                "MP4下载链接": mp4_url if mp4_url else "无法获取"
            }
            
            import re
            # 生成文件名基础
            filename_base = re.sub(r'[\\/:*?"<>|]', '_', f"{video_info['标题']}_{video_info['发布日期']}")
            # 下载视频
            ydl_opts = {
                'format': mp4_format,
                'outtmpl': os.path.join(download_dir, f"{filename_base}.mp4"),
                'quiet': False
            }
            
            if cookies_file:
                ydl_opts['cookiefile'] = cookies_file
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                print(f"视频已下载到: {ydl_opts['outtmpl']}")
                
                mp4_path = os.path.join(download_dir, f"{filename_base}.mp4")

                # 生成说明文件
                info_file = os.path.join(download_dir, f"{filename_base}.txt")
                with open(info_file, 'w', encoding='utf-8') as f:
                    for key, value in video_info.items():
                        f.write(f"{key}: {value}\n")
                print(f"视频信息已保存到: {info_file}")
                    
            except Exception as e:
                print(f"视频下载失败: {str(e)}")
                if "ffmpeg" in str(e).lower():
                    print("提示: 需要安装ffmpeg以支持高质量视频下载")
                    print("安装方法: https://ffmpeg.org/download.html")
                return
        
        # 2. 转换为MP3
        mp3_path = convert_mp4_to_mp3(mp4_path)
        if not mp3_path:
            raise Exception("MP3转换失败")
        
        # 3. 上传MP3
        mp3_url = upload_mp3(mp3_path)
        
        # 4. 语音转文本
        text = recognize_speech(mp3_url)
        
        # 5. 生成文案文件
        txt_path = os.path.splitext(mp4_path)[0] + "_文案.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"视频标题: {video_info.get('标题', '未知')}\n")
            f.write(f"视频链接: {url}\n\n")
            f.write("视频内容转录:\n")
            f.write(text)
        
        print(f"文案已生成: {txt_path}")
        return txt_path
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube视频文案生成工具')
    parser.add_argument('url', help='YouTube视频链接')
    parser.add_argument('--cookies', help='cookies文件路径', required=False, default=cookies_file)
    
    args = parser.parse_args()
    
    result = download_and_transcribe(args.url, args.cookies)
    if not result:
        print("文案生成失败，请检查错误信息")