#!/usr/bin/env python3
from os import path
from vectordb import Memory
from cmd import Cmd
import sys

memory = Memory("dataset/index/index.vecdb", embeddings="fast")

def window(arr, k):
    for i in range(len(arr) - k + 1):
        yield arr[i*k:i*k + k]

class Search(Cmd):
    prompt = 'search: '
    # intro = ""

    def default(self, query):
        printed_entries = set()
        i = 0
        for entry in memory.search(query, top_n=10):
            if i == 3:
                break
            i += 1
            metadata = entry["metadata"]
            if metadata["id"] in printed_entries:
                continue
            printed_entries.add(metadata["id"])

            title = metadata["title"]
            link = metadata["link"]
            chunk = entry['chunk']
            parts = [part for part in window(chunk.split(" "), 20)]
            for i, part in enumerate(parts):
                message = " ".join(part)
                parts[i] = message 
            chunk = "\n".join(parts[:4])
            print(f"[{title}]({link})", chunk, sep="\n")
            print()

if "-i" in sys.argv:
    Search().cmdloop()

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import srt

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/static/css/pico.min.css':
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open('static/css/pico.min.css', 'rb') as f:
                self.wfile.write(f.read())
            return
        if self.path == '/static/css/pico.min.css.map':
            self.send_response(400)
            self.end_headers()
            return

        parameters = dict(parse.parse_qsl(parse.urlsplit(self.path).query))

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if "q" not in parameters:
            html = f"""
                <!DOCTYPE html>
                <html lang="en" data-theme="dark">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <meta http-equiv="X-UA-Compatible" content="ie=edge">
                    <meta name="theme-color" content="hsl(248, 11%, 12%)"/>
                    <meta name="theme-color" content="hsl(248, 11%, 12%)" media="(prefers-color-scheme: dark)"/>
                    <meta name="theme-color" content="hsl(195, 85%, 41%)" media="(prefers-color-scheme: light)"/>
                    <title>search.local</title>
                    <link rel="stylesheet" href="/static/css/pico.min.css">
                    <style>
                    main {{
                        height: 100%;
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                    :root {{
                        --background-color: hsl(248.6, 11.5%, 12%);
                        --color: hsl(205, 16%, 77%);
                        --muted-color: hsl(248.6, 15.3%, 30.2%);
                        --muted-border-color: hsl(248.6, 15.3%, 14.2%);
                        --primary: hsl(248.6, 12.3%, 50.2%);
                        --primary-hover: hsl(248.6, 30.3%, 70.2%);
                        --primary-focus: hsl(249.4, 12.6%, 20.2%);
                        --blockquote-border-color: var(--muted-border-color);
                        --blockquote-footer-color: var(--muted-color);
                        --form-element-background-color: #1c1b22;
                        --form-element-border-color: #757090;
                        --form-element-color: var(--color);
                        --form-element-placeholder-color: var(--muted-color);
                        --form-element-active-background-color: var(--form-element-background-color);
                        --form-element-active-border-color: var(--primary);
                        --form-element-focus-color: var(--primary-focus);
                        --card-background-color: #1a1920;
                        --card-border-color: var(--card-background-color);
                        --card-box-shadow: 0.5em 0.5em 0rem 0px var(--box-shadow-color);
                        --card-sectionning-background-color: #18232c;
                        color-scheme: dark;
                        --box-shadow-color: hsl(248.6, 12.3%, 5.2%);
                    }}
                    </style>
                </head>
                <body>
                    <main class="container">
                        <section id="search">
                            <h1 style="text-align:center;color:var(--primary-hover);">search.local</h1>
                            <form action="" method="get">
                                <input style="min-width:50vw" autofocus type="text" name="q" id="q" placeholder='search' required />
                            </form>
                        </section>
                    </main>
                </body>
                </html>
            """
            self.wfile.write(bytes(html, "utf-8"))
            return

        query = parameters["q"]
        query_lowered_parts = query.lower().split(" ")
        printed_entries = set()
        results = []
        for entry in memory.search(query, top_n=int(parameters["n"]) if "n" in parameters else 20):
            metadata = entry["metadata"]
            if metadata["id"] in printed_entries:
                continue
            printed_entries.add(metadata["id"])

            title = metadata["title"]
            link = metadata["link"]
            chunk = entry['chunk']
            words = chunk.split(" ")
            for i, word in enumerate(words):
                if word.lower().strip(",") in query_lowered_parts:
                    words[i] = f"<em>{word}</em>"
            transcript = ""
            if path.exists(f"./dataset/youtube/transcript-srt/{metadata['id']}.wav.srt"):
                with open(f"./dataset/youtube/transcript-srt/{metadata['id']}.wav.srt") as f:
                    transcript = list(srt.parse(f.read()))
                parts = []
                for line in transcript:
                    parts.append(f"""
                        <div>
                            <div class="time">
                                <span>{str(line.start).split('.')[0]}</span>
                                <span>--&gt</span>
                                <span>{str(line.end).split('.')[0]}</span>
                            </div>
                            <p>{line.content}</p>
                        </div>
                    """)
                transcript = "".join(parts)
            # else:
            #     with open(f"./dataset/youtube/transcript/{metadata['id']}.wav.txt") as f:
            #         transcript = f.read()

            if transcript: 
                transcript = f"""
                    <details>
                        <summary>full transcript</summary>
                        {transcript}
                    </details>
                """

            subtitle = None
            if metadata["published"]:
                published = metadata["published"]
                subtitle = f"<h3 class='fix-date'>{published}<h3>"

            chunk = " ".join(words)
            if metadata["type"] == "youtube":
                chunk = " ".join(chunk.split(" ")[:40]) + "..."
                results.append(f"""
                    <article>
                        <hgroup>
                            <h2><a href='{link}'>{title}</a></h2>
                            {subtitle}
                        </hgroup>
                        <blockquote>
                            <p>{chunk}</p>
                            <footer>
                                <cite>- {metadata['author']}</cite>
                            </footer>
                        </blockquote>
                        {transcript}
                    </article>
                """)
            else:
                results.append(f"""
                    <article>
                        <hgroup>
                            <h2><a href='{link}'>{title}</a></h2>
                            {subtitle}
                        </hgroup>
                        <blockquote>
                            <p>{metadata['summary']}</p>
                            <footer>
                                <cite>- {metadata['author']}</cite>
                            </footer>
                        </blockquote>
                        <details>
                            <summary>matching search</summary>
                            <p>{chunk}<p>
                        </details>
                        {transcript}
                    </article>
                """)

        html = f"""
            <!DOCTYPE html>
            <html lang="en" data-theme="dark">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="ie=edge">
                <meta name="theme-color" content="hsl(195, 85%, 41%)" />
                <title>search.local</title>
                <link rel="stylesheet" href="/static/css/pico.min.css">
                <style>
                    :root {{
                        --background-color: unset;
                        --color: hsl(205, 16%, 77%);
                        --muted-color: hsl(248.6, 15.3%, 30.2%);
                        --muted-border-color: hsl(248.6, 15.3%, 14.2%);
                        --primary: hsl(248.6, 12.3%, 50.2%);
                        --primary-hover: hsl(248.6, 30.3%, 70.2%);
                        --primary-focus: hsl(249.4, 12.6%, 20.2%);
                        --primary-inverse: #fff;
                        --secondary: hsl(205, 15%, 41%);
                        --secondary-hover: hsl(205, 10%, 50%);
                        --secondary-focus: rgba(115, 130, 140, 0.25);
                        --secondary-inverse: #fff;
                        --contrast: hsl(205, 20%, 94%);
                        --contrast-hover: #fff;
                        --contrast-focus: rgba(115, 130, 140, 0.25);
                        --contrast-inverse: #000;
                        --mark-background-color: #d1c284;
                        --mark-color: #11191f;
                        --ins-color: #388e3c;
                        --del-color: #c62828;
                        --blockquote-border-color: var(--muted-border-color);
                        --blockquote-footer-color: var(--muted-color);
                        --button-box-shadow: 0 0 0 rgba(0, 0, 0, 0);
                        --button-hover-box-shadow: 0 0 0 rgba(0, 0, 0, 0);
                        --form-element-background-color: #1c1b22;
                        --form-element-border-color: #757090;
                        --form-element-color: var(--color);
                        --form-element-placeholder-color: var(--muted-color);
                        --form-element-active-background-color: var(--form-element-background-color);
                        --form-element-active-border-color: var(--primary);
                        --form-element-focus-color: var(--primary-focus);
                        --form-element-disabled-background-color: hsl(205, 25%, 23%);
                        --form-element-disabled-border-color: hsl(205, 20%, 32%);
                        --form-element-disabled-opacity: 0.5;
                        --form-element-invalid-border-color: #b71c1c;
                        --form-element-invalid-active-border-color: #c62828;
                        --form-element-invalid-focus-color: rgba(198, 40, 40, 0.25);
                        --form-element-valid-border-color: #2e7d32;
                        --form-element-valid-active-border-color: #388e3c;
                        --form-element-valid-focus-color: rgba(56, 142, 60, 0.25);
                        --switch-background-color: #374956;
                        --switch-color: var(--primary-inverse);
                        --switch-checked-background-color: var(--primary);
                        --range-border-color: #24333e;
                        --range-active-border-color: hsl(205, 25%, 23%);
                        --range-thumb-border-color: var(--background-color);
                        --range-thumb-color: var(--secondary);
                        --range-thumb-hover-color: var(--secondary-hover);
                        --range-thumb-active-color: var(--primary);
                        --table-border-color: var(--muted-border-color);
                        --table-row-stripped-background-color: rgba(115, 130, 140, 0.05);
                        --code-background-color: #18232c;
                        --code-color: var(--muted-color);
                        --code-kbd-background-color: var(--contrast);
                        --code-kbd-color: var(--contrast-inverse);
                        --code-tag-color: hsl(330, 30%, 50%);
                        --code-property-color: hsl(185, 30%, 50%);
                        --code-value-color: hsl(40, 10%, 50%);
                        --code-comment-color: #4d606d;
                        --accordion-border-color: var(--muted-border-color);
                        --accordion-active-summary-color: var(--primary);
                        --accordion-close-summary-color: var(--color);
                        --accordion-open-summary-color: var(--muted-color);
                        --card-background-color: #1a1920;
                        --card-border-color: var(--card-background-color);
                        --card-box-shadow: 0.5em 0.5em 0rem 0px var(--box-shadow-color);
                        --card-sectionning-background-color: #18232c;
                        --dropdown-background-color: hsl(205, 30%, 15%);
                        --dropdown-border-color: #24333e;
                        --dropdown-box-shadow: var(--card-box-shadow);
                        --dropdown-color: var(--color);
                        --dropdown-hover-background-color: rgba(36, 51, 62, 0.75);
                        --modal-overlay-background-color: rgba(36, 51, 62, 0.8);
                        --progress-background-color: #24333e;
                        --progress-color: var(--primary);
                        --loading-spinner-opacity: 0.5;
                        --tooltip-background-color: var(--contrast);
                        --tooltip-color: var(--contrast-inverse);
                        color-scheme: dark;
                        --box-shadow-color: hsl(248.6, 12.3%, 5.2%);
                    }}
                </style>
            </head>
            <body>
                <header class="container">
                    <nav id="search">
                        <ul>
                            <li><h1 style="margin:0;"><a href="/">search.local</a></h1></li>
                        </ul>
                        <ul>
                            <li>
                                <form style="margin:0;" action="" method="get">
                                    <input type="text" name="q" id="q" value='{parameters["q"]}' placeholder='search' required />
                                </form>
                            </li>
                        </ul>
                    </nav>
                </header>
                <main class="container">
                    <section>{" ".join(results)}</section>
                </main>
                <script>
                "use strict";
                (() => {{
                    const fixDates = document.querySelectorAll('.fix-date');
                    if (fixDates) fixDates.forEach(item => {{
                        try {{
                            item.innerText = new Date(item.innerText).toLocaleDateString();
                            item.classList.remove('fix-date');
                        }} catch {{}}
                    }})
                }})();
                </script>
            </body>
            </html>
        """
        self.wfile.write(bytes(html, "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
