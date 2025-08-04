# YouTube Video Info API

A simple HTTP service to fetch YouTube video information and MP3 download links.

## Features
- Get basic video information (title, author, views, etc.)
- Retrieve MP3 download link
- Simple RESTful API interface

## Requirements
- Python 3.6+
- yt-dlp
- Flask

## Installation
```bash
pip install yt-dlp flask
```

## Usage
1. Start the server:
```bash
python youtube_api.py
```

2. Make a GET request:
```
http://localhost:8000/?url=<youtube_url>
```

## Response Format
```json
{
    "code": "success/error",
    "data": {
        "title": "video title",
        "author": "uploader name",
        "views": "view count",
        "publish_date": "upload date",
        "duration": "duration in seconds",
        "description": "video description",
        "mp3_url": "MP3 download link"
    },
    "msg": "error message if any",
    "src_url": "original YouTube URL"
}
```

## Example
Request:
```
http://localhost:8000/?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Response:
```json
{
    "code": "success",
    "data": {
        "title": "Never Gonna Give You Up",
        "author": "Rick Astley",
        "views": "123456789",
        "publish_date": "20091025",
        "duration": "212",
        "description": "Official video...",
        "mp3_url": "https://..."
    },
    "msg": "",
    "src_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

## License
MIT