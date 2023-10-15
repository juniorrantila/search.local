#!/usr/bin/env python3
from os import listdir
from vectordb import Memory
import json
from bs4 import BeautifulSoup

memory = Memory("dataset/index.vecdb", embeddings="fast")
indexed_entrys = set(file["metadata"]["id"] for file in memory.memory)

def strip_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    for data in soup(['style', 'script']):
        data.decompose()
    return " ".join(soup.stripped_strings)

new_entries = []
feeds = listdir("./dataset/blogs/feeds")
for i, feed in enumerate(feeds):
    print(f"checking {i}/{len(feeds)}")
    try:
        with open(f"./dataset/blogs/feeds/{feed}") as f:
            feed_content = json.load(f)
        entries = feed_content["entries"]
        for entry in entries:
            if "link" not in entry:
                continue
            if "id" in entry:
                entry_id = str(entry["id"]).strip(":/?")
            else:
                entry_id = str(entry["link"]).strip(":/?")
            if entry_id in indexed_entrys:
                continue
            new_entries.append(entry)
    except KeyboardInterrupt:
        exit(0)
    except:
        print(f"failed {feed}")
        continue

for i, entry in enumerate(new_entries):
    if i % 100 == 0:
        print(f"indexing {i}/{len(new_entries)}")

    if "id" in entry:
        entry_id = str(entry["id"]).strip(":/?")
    else:
        entry_id = str(entry["link"]).strip(":/?")

    if "author" in entry:
        author = entry["author"]
    elif "authors" in entry:
        author = " ".join(n["name"] for n in entry["authors"])
    elif "author_detail" in entry:
        author = entry["author_detail"]["name"]
    else:
        author = None

    if "tags" in entry:
        tags = [term for term in entry["tags"]]
    else:
        tags = None

    if "summary" in entry:
        summary = " ".join(strip_tags(entry["summary"]).split(" ")[:20])
    else:
        summary = None

    if "published" in entry:
        published = entry["published"]
    elif "updated" in entry:
        published = entry["updated"]
    else:
        published = None

    if "title" in entry:
        title = entry["title"]
    else:
        title = None

    try:
        meta = {
            "type": "blog",
            "id": entry_id,
            "title": title,
            "link": entry["link"],
            "author": author,
            "published": published,
            "tags": tags,
            "summary": summary,
        }
    except:
        print(entry)
        raise
    if "content" in entry:
        content = [strip_tags(c["value"]) for c in entry["content"]]
    else:
        content = None

    try:
        if content is not None:
            memory.append(content, metadata=[meta])
        if meta["title"] is not None:
            memory.append(meta["title"], metadata=[meta])
        if meta["summary"] is not None:
            memory.append(meta["summary"], metadata=[meta])
        if meta["tags"] is not None:
            all_tags = ""
            for tag in meta["tags"]:
                if isinstance(tag, dict):
                    tag = tag["term"]
                all_tags = f"{all_tags} tag"
                memory.append(tag, metadata=[meta])
            memory.append(all_tags, metadata=[meta])
        if meta["author"] is not None:
            memory.append(meta["author"], metadata=[meta])
    except UnicodeDecodeError:
        continue
    except TypeError as e:
        print(e)
        continue
    except KeyboardInterrupt:
        exit(0)
    if i % 10000 == 0 and i != 0:
        print("saving to disk")
        memory.save_to_disk()
        print("done")
print("saving to disk")
memory.save_to_disk()
print("done")
