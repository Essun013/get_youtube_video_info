import os
import datetime
from moviepy.editor import VideoFileClip

def convert_single_mp4_to_mp3(mp4_path):
    """
    将单个MP4文件转换为MP3音频文件
    :param mp4_path: MP4文件完整路径
    :return: 生成的MP3文件路径
    """
    try:
        # 获取文件名和目录
        dir_path = os.path.dirname(mp4_path)
        filename = os.path.basename(mp4_path)
        
        # 生成输出文件名（带时间戳）
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"{os.path.splitext(filename)[0]}_{current_time}.mp3"
        output_path = os.path.join(dir_path, output_filename)
        
        # 加载视频文件并提取音频
        video = VideoFileClip(mp4_path)
        audio = video.audio
        
        # 保存为MP3文件
        audio.write_audiofile(output_path)
        print(f"成功转换: {filename} -> {output_filename}")
        
        # 关闭文件句柄
        audio.close()
        video.close()
        
        return output_path
    except Exception as e:
        print(f"转换失败 {mp4_path}: {str(e)}")
        return None

def convert_mp4_to_mp3(input_folder):
    """
    将指定文件夹下的所有MP4文件转换为MP3音频文件
    :param input_folder: 包含MP4文件的文件夹路径
    """
    # 确保输出文件夹存在
    output_folder = os.path.join(input_folder, "mp3_output")
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.mp4'):
            # 获取当前时间作为文件名后缀
            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            # 构建输入输出文件路径
            input_path = os.path.join(input_folder, filename)
            output_filename = f"{os.path.splitext(filename)[0]}_{current_time}.mp3"
            output_path = os.path.join(output_folder, output_filename)
            
            try:
                # 加载视频文件并提取音频
                video = VideoFileClip(input_path)
                audio = video.audio
                
                # 保存为MP3文件
                audio.write_audiofile(output_path)
                print(f"成功转换: {filename} -> {output_filename}")
                
                # 关闭文件句柄
                audio.close()
                video.close()
            except Exception as e:
                print(f"转换失败 {filename}: {str(e)}")

if __name__ == "__main__":
    # 用户输入选项
    choice = input("请选择模式: 1-转换单个文件 2-转换整个文件夹\n")
    
    if choice == "1":
        file_path = input("请输入MP4文件完整路径: ")
        if os.path.isfile(file_path):
            convert_single_mp4_to_mp3(file_path)
        else:
            print("错误: 文件不存在")
    elif choice == "2":
        folder_path = input("请输入包含MP4文件的文件夹路径: ")
        if os.path.isdir(folder_path):
            convert_mp4_to_mp3(folder_path)
        else:
            print("错误: 指定的路径不存在或不是一个文件夹")
    else:
        print("错误: 无效选择")