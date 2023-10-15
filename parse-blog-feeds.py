#!/usr/bin/env python3
import feedparser
import json

import asyncio

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped

with open("./dataset/kagi/smallweb.txt") as f:
    links = f.readlines()

links_len = len(links)
done = 0
def update():
    global done
    global links_len
    done += 1
    print(f"{done}/{links_len}")


@background
def save_link(name: str, link: str):
    rss_feed = feedparser.parse(link)
    try:
        json_string = json.dumps(rss_feed)
    except:
        return
    with open(f"dataset/blogs/{name}.json", "w+") as f:
        f.write(json_string)
    update()

links_len = len(links)
for i, link in enumerate(links):
    print(f"started {i}/{links_len}")
    save_link(str(i), link)

# rss_feed = feedparser.parse(links[102])
# print(rss_feed.entries[0].summary)
