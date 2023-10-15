#!/usr/bin/env python3
from os import listdir, system
import srt

transcribed_files = [f[:-len(".txt")] for f in listdir('./dataset/youtube/transcript')]
audio_files = set(f for f in listdir("./dataset/youtube/audio") if f.endswith(".wav"))
audio_files = [file for file in audio_files.difference(transcribed_files)]

for i, file in enumerate(audio_files):
    print(f"{i}/{len(audio_files)}")
    system(f"./vendor/whisper.cpp/build/bin/main -l en -osrt -f ./dataset/youtube/audio/{file} -m ./dataset/models/ggml-tiny.en.bin -of ./dataset/youtube/transcript-srt/{file}")
    with open(f"./dataset/youtube/transcript-srt/{file}.srt") as f:
        lines = [e.content for e in srt.parse(f.read())]
    transcript = "".join(lines)
    with open(f"./dataset/youtube/transcript/{file}.txt", "w+") as f:
        f.write(transcript)

    transcribed_files = [f[:-len(".txt")] for f in listdir('./dataset/youtube/transcript')]
    audio_files2 = set(f for f in listdir("./dataset/youtube/audio") if f.endswith(".wav"))
    audio_files2 = audio_files2.difference(transcribed_files)
    audio_files2 = audio_files2.difference(audio_files)
    print(f"{len(audio_files2)} new files")
    for audio_file in audio_files2:
        audio_files.append(audio_file)
