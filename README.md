# YouTube 视频信息获取与转录工具集

一个功能完整的YouTube视频处理工具集，支持视频下载、音频转换、语音转文本等多种功能。

## 📋 项目概述

本项目提供了一套完整的YouTube视频处理解决方案，包括：
- 获取YouTube视频基本信息
- 下载YouTube视频（MP4格式）
- 视频转音频（MP3格式）
- 音频语音识别转文本
- Web API服务接口
- 一键式视频转文案功能

## ✨ 核心功能

### 1. 视频信息获取
- 提取视频标题、作者、观看次数、发布日期等基本信息
- 获取视频描述和时长信息
- 支持Cookie认证访问受限视频

### 2. 视频下载
- 支持YouTube视频下载为MP4格式
- 自动生成规范化文件名（标题+发布日期）
- 自动创建下载目录和说明文件
- 支持Cookie文件绕过登录限制

### 3. 音频转换
- MP4视频文件转MP3音频文件
- 支持单文件和批量转换
- 自动添加时间戳避免文件名冲突

### 4. 语音识别
- 集成阿里百炼语音识别API
- 支持MP3文件自动上传到公网服务器
- 异步任务处理，支持长音频文件
- 自动生成转录文本文件

### 5. 一键式处理
- YouTube链接 → 视频下载 → 音频转换 → 语音识别 → 文案生成
- 全自动化流程，一条命令完成所有操作

### 6. Web API服务
- 提供RESTful API接口
- 支持HTTP GET请求获取视频信息
- 返回标准JSON格式数据

## 🛠️ 技术栈

- **Python 3.6+** - 主要开发语言
- **yt-dlp** - YouTube视频下载和信息提取
- **moviepy** - 视频音频处理
- **Flask** - Web API框架
- **requests** - HTTP请求处理
- **阿里百炼API** - 语音识别服务

## 📦 安装依赖

```bash
# 安装Python依赖包
pip install yt-dlp
pip install requests
pip install flask
pip install moviepy
pip install --upgrade yt-dlp

# 安装FFmpeg（视频处理必需）
# Windows: 下载并安装 https://ffmpeg.org/download.html
# Ubuntu/Debian: sudo apt install ffmpeg
# CentOS/RHEL: sudo yum install ffmpeg
```

## 🚀 使用方法

### 1. 获取视频基本信息

```bash
python get_youtube_info.py
# 根据提示输入YouTube视频链接
```

### 2. 下载YouTube视频

```bash
# 基本下载
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 使用Cookie文件（访问受限视频）
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies "path/to/cookies.txt"
```

### 3. 视频转音频

```bash
# 单文件转换
python mp4_to_mp3_converter.py
# 选择模式1，输入MP4文件路径

# 批量转换
python mp4_to_mp3_converter.py
# 选择模式2，输入包含MP4文件的文件夹路径
```

### 4. 音频转文本

```bash
python mp3_to_text.py
# 输入MP3文件完整路径
```

### 5. 一键式视频转文案

```bash
# 最强功能：一条命令完成 视频下载→音频转换→语音识别→文案生成
python youtube_transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID"

# 使用自定义Cookie文件
python youtube_transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID" --cookies "path/to/cookies.txt"
```

### 6. Web API服务

```bash
# 启动Web服务
python youtube_api.py

# 访问API接口
curl "http://localhost:8000/?url=https://www.youtube.com/watch?v=VIDEO_ID"

# 使用Cookie认证
curl "http://localhost:8000/?url=https://www.youtube.com/watch?v=VIDEO_ID&cookies_file=/path/to/cookies.txt"
```

## 📁 项目结构

```
get_youtube_video_info/
├── README.md                    # 项目说明文档
├── youtube_transcriber.py       # 🌟 核心工具：一键视频转文案
├── youtube_downloader.py        # YouTube视频下载器
├── youtube_api.py              # Web API服务接口
├── get_youtube_info.py         # 视频信息获取工具
├── mp4_to_mp3_converter.py     # 视频转音频工具
├── mp3_to_text.py              # 音频转文本工具
├── www.youtube.com_cookies.txt # YouTube Cookie文件样例
├── deploy_python.txt           # Python环境部署记录
├── download_mp4/               # 视频下载目录
└── __pycache__/               # Python缓存目录
```

## 🔧 配置说明

### 阿里百炼API配置
在使用语音识别功能前，需要配置阿里百炼API：

1. 在 `mp3_to_text.py` 和 `youtube_transcriber.py` 中设置：
```python
API_KEY = "your-api-key-here"  # 替换为您的API密钥
```

2. 配置MP3文件上传服务器地址：
```python
PUBLIC_MP3_URL = "https://your-server.com/mp3/"  # 替换为您的服务器地址
```

### Cookie文件配置
对于需要登录才能访问的YouTube视频：

1. 使用Chrome浏览器登录YouTube
2. 安装Cookie导出插件（如"Get cookies.txt"）
3. 导出cookies.txt文件
4. 在命令行中指定Cookie文件路径

## 📊 API响应格式

Web API返回标准JSON格式：

```json
{
    "code": "success",
    "data": {
        "title": "视频标题",
        "author": "上传者",
        "views": "观看次数",
        "publish_date": "发布日期",
        "duration": "视频时长（秒）",
        "description": "视频描述",
        "mp3_url": "MP3下载链接"
    },
    "msg": "错误信息（如有）",
    "src_url": "原始YouTube链接"
}
```

## 🎯 使用场景

### 内容创作者
- 快速获取竞品视频文案进行分析
- 将视频内容转换为文字进行二次创作
- 批量处理视频素材

### 学习研究
- 将教学视频转换为文字笔记
- 提取讲座和会议的文字记录
- 语言学习材料的文本化

### 商业应用
- 市场调研视频的内容分析
- 客户反馈视频的文字整理
- 培训材料的文档化

## ⚠️ 注意事项

1. **版权声明**：请遵守YouTube的使用条款和版权法规，仅下载您有权使用的内容
2. **API限制**：阿里百炼API有调用频率限制，请合理使用
3. **网络依赖**：工具需要稳定的网络连接，建议在网络环境良好时使用
4. **文件大小**：大文件处理可能需要较长时间，请耐心等待
5. **服务器要求**：语音识别功能需要将MP3文件上传到可公网访问的服务器

## 🔄 更新日志

- **v1.0** - 基础功能实现
- **v1.1** - 添加Web API接口
- **v1.2** - 集成语音识别功能
- **v1.3** - 实现一键式视频转文案功能
- **v1.4** - 优化错误处理和用户体验

## 📄 许可证

MIT License - 详见LICENSE文件

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📞 支持

如果您在使用过程中遇到问题，请：
1. 查看文档和注意事项
2. 检查依赖是否正确安装
3. 确认网络连接和API配置
4. 提交详细的Issue报告

---

**🌟 推荐使用 `youtube_transcriber.py` 实现一键式视频转文案，这是本项目的核心功能！**