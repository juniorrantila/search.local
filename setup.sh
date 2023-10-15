#!/bin/sh
set -xe

mkdir -p ./dataset/blogs/feeds
mkdir -p ./dataset/wikipedia
mkdir -p ./dataset/kagi
mkdir -p ./dataset/youtube/transcript
mkdir -p ./dataset/youtube/feeds
mkdir -p ./dataset/youtube/audio
mkdir -p ./dataset/youtube/transcript-srt
mkdir -p ./dataset/index

mkdir -p ./vendor/whisper.cpp/build
cmake -S ./vendor/whisper.cpp -B ./vendor/whisper.cpp/build
ninja -C ./vendor/whisper.cpp/build