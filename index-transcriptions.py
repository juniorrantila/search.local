#!/usr/bin/env python3
from os import listdir
from vectordb import Memory
import json

memory = Memory("dataset/index/index.vecdb", embeddings="fast")

indexed_files = set(file["metadata"]["id"] for file in memory.memory)

video_metadata = dict()
feeds = listdir("./dataset/youtube/feeds")
new_transcribed_ids = set(name[:-len(".wav.txt")] for name in listdir('./dataset/youtube/transcript'))
new_transcribed_ids = new_transcribed_ids.difference(indexed_files)

for feed in feeds:
    with open(f"./dataset/youtube/feeds/{feed}") as f:
        feed_content = json.load(f)
    entries = feed_content["entries"]
    for entry in entries:
        video_id = entry["yt_videoid"]
        if video_id not in new_transcribed_ids:
            continue
        video_metadata[video_id] = {
            "type": "youtube",
            "id": video_id,
            "title": entry["title"],
            "link": entry["link"],
            "author": entry["author"],
            "published": entry["published"],
        }

for i, video_id in enumerate(new_transcribed_ids):
    try:
        print(f"indexing {i}/{len(new_transcribed_ids)}")
        with open(f"./dataset/youtube/transcript/{video_id}.wav.txt") as f:
            content = f.read()
        memory.append(content, metadata=video_metadata[video_id])
    except UnicodeDecodeError:
        continue
    except TypeError as e:
        print(e)
        continue
    except KeyError as e:
        print(e)
        continue
    except KeyboardInterrupt:
        exit(0)
    if i % 100 == 0:
        memory.save_to_disk()
memory.save_to_disk()
