---
date: '2006-11-08'
title: Transcode commands
category: English
tags: Audio, CLI, Linux, subtitle, transcode, Video, avimerge, tcprobe, tccat, mp4, vid.stab, mkv, x264
---

```{admonition} Unmaintained project
:class: warning
The [`transcode` CLI and its associated tools](https://web.archive.org/web/20200806075355/https://bitbucket.org/achurch_/transcode/wiki/Home) are no longer maintained.

I recommend to use [FFmpeg]({filename}/2006/video-commands.md) instead.
```

- Get information about a video:

  ```shell-session
  $ tcprobe -i ./video.avi
  ```

- Merge multiple video into one:

  ```shell-session
  $ avimerge -i part1.avi part2.avi -o big-file.avi
  ```

- Extract the raw subtitle stream. The `-a 0x21` option correspond to the
  subtitle stream's hexadecimal number (= 0x20 + id of the stream):

  ```shell-session
  $ tccat -i /space/st-tng/dic1/ -T 1 -L | tcextract -x ps1 -t vob -a 0x22 > subs-en
  ```

- List export video codecs:

  ```shell-session
  $ transcode -i . -y ffmpeg -F list
  ```

- Extract all frames of a video and save them as `.jpg`:

  ```shell-session
  $ transcode -i video.avi -y im
  ```

- Batch stabilization script:

  ```bash
  SEARCH_FOLDER="/home/kevin/project/raw_sources"
  DEST_FOLDER="/home/kevin/project/stabilized"

  for FILE_PATH in $(find "$SEARCH_FOLDER" -name "*.mp4"); do
  	FILE_NAME=$(basename "$FILE_PATH")

  	STAB_FILE="$DEST_FOLDER/$FILE_NAME.trf"
  	if [ ! -e "$STAB_FILE" ]; then
  		# vis.stab's deshake/stabilize documentation:
  		# https://github.com/georgmartius/vid.stab/blob/36173857bfc0fa111983a5934f2cc6322969e928/transcode/filter_deshake.c#L75-L106
  		transcode -J stabilize=result="$STAB_FILE" -i "$FILE_PATH" -y null,null -o dummy
  	fi

  	FINAL_FILE="$DEST_FOLDER/$FILE_NAME-stabilized.mkv"

  	if [ ! -e "$FINAL_FILE" ]; then

  		# Create a stabilized stream of JPG files at 100% quality.
  		FRAME_BASEPATH="$DEST_FOLDER/$FILE_NAME.stabilized_"
  		# vid.stab's transform documentation:
  		# https://github.com/georgmartius/vid.stab/blob/36173857bfc0fa111983a5934f2cc6322969e928/src/transform.h#L122-L149
  		transcode -J transform=input="$STAB_FILE" -i "$FILE_PATH" -y jpg,null -F 100 -o "$FRAME_BASEPATH"

  		# Convert to a lossless h264 video in 4:2:0 color space.
  		FRAME_RATE=$(tcprobe -i "$FILE_PATH" | grep "frame rate:" | cut -d ':' -f 2 | cut -d ' ' -f 3)
  		avconv -r $FRAME_RATE -i "$FRAME_BASEPATH%06d.jpg" -c:v libx264 -pix_fmt yuv420p -preset veryfast -qp 0 "$FINAL_FILE"

  		find "$DEST_FOLDER" -name "$FRAME_BASENAME*.jpg" -delete

  	fi

  done
  ```
