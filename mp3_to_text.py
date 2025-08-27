import os
import requests
import json
import uuid
import time, random
from urllib.parse import urljoin

# 功能：语音转文本mp3_to_Text，先把MP3文件上传到指定服务器地址，然后使用RESTful API方法调用阿里百炼语音识别paraformer-v2模型，
# 成功返回纯文本并写入本地文件中，本地文件命名方式mp3名+.txt

# 配置参数
API_KEY = "sk-24fb02c39f784ff888b7a3b3db5ed6e6"
API_TRANS_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
API_TASK_STATUS_URL = "https://dashscope.aliyuncs.com/api/v1/tasks"
PUBLIC_MP3_URL = "https://www.dfs521.com/mp3/"
MODEL="paraformer-v2"
# E:\project\get_youtube_video_info\download_mp4\专家说楼市进入二次下跌__中国楼市到底有没有泡沫_20250821.mp3

def upload_mp3(mp3_path):
    """上传MP3文件到公网地址并确认可访问"""
    try:
        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}.mp3"
        upload_url = urljoin(PUBLIC_MP3_URL, filename)
        
        # 1. 上传文件
        with open(mp3_path, "rb") as f:
            response = requests.put(upload_url, data=f)
        if response.status_code != 201 and response.status_code != 204:
            raise Exception(f"文件上传失败: {response.text}")
        
        # 2. 异步验证文件可访问性（最多重试5次）
        max_retries = 5
        for i in range(max_retries):
            try:
                head_resp = requests.head(upload_url)
                if head_resp.status_code == 200:
                    print(f"文件已确认可访问: {upload_url}")
                    return upload_url
                
                print(f"等待文件就绪({i+1}/{max_retries})...")
                time.sleep(8)  # 等待8秒后重试
                
            except Exception as e:
                print(f"验证失败({i+1}/{max_retries}): {str(e)}")
                time.sleep(8)
                
        raise Exception(f"文件未就绪: 超过最大重试次数{max_retries}")
        
    except Exception as e:
        raise Exception(f"上传MP3文件失败: {str(e)}")

def recognize_speech(mp3_url):
    """调用阿里百炼API进行语音识别"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"  # 启用异步模式
    }
    
    # 验证URL格式（确保以http://或https://开头）
    if not mp3_url.startswith("http"):
        raise Exception(f"无效的URL格式: {mp3_url}")
    
    # 打印调试信息
    print(f"正在调用阿里百炼API，URL: {mp3_url}，录音文件识别大模型：{MODEL}")
    
    payload = {
        "model": MODEL,  # 使用 paraformer-v2 模型
        "input": {
            "file_urls": [mp3_url]  # 必填字段，需传入数组
        },
        "parameters": {
            "enable_timestamp": False  # 禁用时间戳
        }
    }
    
    try:
        response = requests.post(API_TRANS_URL, headers=headers, json=payload, timeout=50)
        
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                task_status = result['output']['task_status']
                
                # 轮询任务状态
                max_retries = 30
                for _ in range(max_retries):
                    # 20~30秒随机生成
                    retry_interval = random.randint(20, 30)
                    if task_status == "SUCCEEDED":
                        task_result = requests.post(
                            f"{API_TASK_STATUS_URL}/{task_id}",
                            headers=headers,
                            timeout=60
                        ).json()
                        print(f"taskId（{task_id}）任务状态: {task_status}, 第{_+1}次尝试，当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}, 转换成功！")
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
                                    raise Exception(f"无效的转录数据格式: {transcription_data}")
                            else:
                                raise Exception(f"获取转录数据失败: {transcription_response.text}")
                        else:
                            raise Exception(f"任务结果格式异常: {task_result}")
                    elif task_status == 'RUNNING' or task_status == 'PENDING':
                        print(f"taskId（{task_id}）任务状态: {task_status}, 第{_+1}次尝试，当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}, 等待 {retry_interval} 秒后重试...")
                    elif task_status == "FAILED":
                        raise Exception(f"语音识别任务失败: {result}")
                    
                    time.sleep(retry_interval)
                    
                    # 重新获取任务状态
                    task_status = requests.post(
                        f"{API_TASK_STATUS_URL}/{task_id}",
                        headers=headers,
                        timeout=60
                    ).json()['output']['task_status']
                
                raise Exception(f"语音识别任务未完成: 超过最大轮询次数{max_retries}")
            else:
                raise Exception(f"API响应格式异常: {result}")
        else:
            raise Exception(f"语音识别失败: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API请求异常: {str(e)}")

def mp3_to_text(mp3_path):
    """主函数：MP3转文本"""
    try:
        # 1. 上传MP3到公网
        mp3_url = upload_mp3(mp3_path)
        print(f"MP3文件已上传到: {mp3_url}")
        
        # 2. 调用API识别
        text = recognize_speech(mp3_url)
        
        # 3. 生成TXT文件
        txt_path = os.path.splitext(mp3_path)[0] + "_文案.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"文本已保存到: {txt_path}")
        return txt_path
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return None

if __name__ == "__main__":
    mp3_path = input("请输入MP3文件完整路径: ")
    if os.path.isfile(mp3_path):
        mp3_to_text(mp3_path)
    else:
        print("错误: 文件不存在")