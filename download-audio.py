#!/usr/bin/env python3
import yt_dlp
import json
from os import listdir

ydl_opts = {
    'outtmpl': 'dataset/youtube/audio/%(id)s.%(ext)s',
    'format': 'worstaudio/worst',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
    }],
   'postprocessor_args': [
        '-ar', '16000',
        '-ac', '1',
    ],
   'prefer_ffmpeg': True,
}

videos = []

downloaded_video_ids = set(file[:-4] for file in listdir('dataset/youtube/audio'))
json_files = listdir('dataset/youtube/feeds')
for file in json_files:
    with open(f"./dataset/youtube/feeds/{file}") as f:
        feed = json.load(f)
        for entry in feed['entries']:
            video_id = entry['link'].split("?v=")[1]
            if video_id ==  "ORDDydi2pks":
                continue
            if video_id == '5lyJHMS8wTI':
                continue
            if video_id == 'JQ9KAQrq18U':
                continue
            if video_id == 'MZp8TkxNT6I':
                continue
            if video_id == 'en5kEuUOMZE':
                continue
            if video_id == '-dSWQ1sy-lw':
                print(entry)
                continue
            if video_id not in downloaded_video_ids:
                videos.append(entry['link'])

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(videos)
