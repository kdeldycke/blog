---
date: '2006-11-01'
title: Audio commands
category: English
tags: ALAC, ASF, Audio, CLI, cue-list, FLAC, Linux, lossless, midi, Ogg, shntool, sox, PCM, id3v2, Apple Music
---

- Convert `.wma` file to 192 kpbs `.mp3`:

  ```shell-session
  $ ffmpeg -i audio.wma -b:a 192k audio.mp3
  ```

- Convert all `.wma` files to VBR `.mp3` at [quality range number
  #4](https://trac.ffmpeg.org/wiki/Encode/MP3#VBREncoding):

  ```shell-session
  $ find . -iname "*.wma" -exec ffmpeg -i "{}" -q:a 4 "{}.mp3" \;
  $ rename 's/\.wma\.mp3/\.mp3/' *.mp3
  ```

- Convert `.ape` file to `.wav`:

  ```shell-session
  $ ffmpeg -i audio.ape audio.wav
  ```

- Split a one-file album flac file into tracks according its cue list:

  ```shell-session
  $ shntool split -f album.cue -o flac album.flac
  ```

- Split a raw `BIN`/`CUE` copy of a CD-DA image and transcode each track as a flac:

  ```shell-session
  $ ffmpeg -f s16le -ar 44.1k -ac 2 -i ./CDDA_COPY.BIN ./cdda.wav
  $ shntool split -f ./CDDA_COPY.CUE -o flac ./cdda.wav
  ```

- Merge several .wav file to one file named `merged.wav`:

  ```shell-session
  $ sox part1.wav part2.wav part3.wav merged.wav
  ```

- Convert `.wav` audio file to ALAC lossless file:

  ```shell-session
  $ ffmpeg -i audio.wav -acodec alac audio.m4a
  ```

- Convert FLAC audio file to Apple Losseless codec (ALAC), while preserving metadata, including embedded cover. This is perfect to import files into Apple Music:

  ```shell-session
  $ ffmpeg -i track.flac -vcodec copy -acodec alac track.m4a
  ```

- Convert `.asf` audio file to PCM wave file:

  ```shell-session
  $ mplayer -vo null -hardframedrop -ao pcm:file=audio.wav audio.asf
  ```

- Convert MIDI file to Ogg/Vorbis:

  ```shell-session
  $ timidity -Ov1S *.mid
  ```

- Extract the Right then Left channel of a stereo .wav file:

  ```shell-session
  $ sox stereo.wav -c 1 rightchan.wav avg -r
  $ sox stereo.wav -c 1 leftchan.wav avg -l
  ```

- Some sox compressor parameters:

  ```shell-session
  $ play audio.wav compand .1,.1 -60,-10 0 0 .1
  $ play audio.wav compand .01,.3 -6,-4,-3,-3,0,-3
  $ play audio.wav compand 0.3,1 -90,-90,-70,-70,-60,-20,0,0 -5 0 0.2
  ```

- Test Alsa audio driver output via gstreamer v0.10:

  ```shell-session
  $ gst-launch-0.10 audiotestsrc ! alsasink
  ```

- Generate cyclic pink noise ([source](https://news.ycombinator.com/item?id=3547169)):

  ```shell-session
  $ play -t sl -r48000 -c2 - synth -1 pinknoise tremolo .1 40 <  /dev/zero
  ```

- Generate background low frequency noise ([source](https://news.ycombinator.com/item?id=3547169)):

  ```shell-session
  $ play -c2 -n synth whitenoise band -n 100 24 band -n 300 100 gain +20
  ```

- Set album tag on all MP3 files found:

  ```shell-session
  $ find . -iname '*.mp3' -print -exec id3v2 --album "Album name" "{}" \;
  ```

Other related resources:

- [Sox examples](https://web.archive.org/web/20061209220211/http://linuxcommand.org/man_pages/soxexam1.html)
- [Audio Processing
  Pipelines](https://web.archive.org/web/20140325123348/https://linuxgazette.net/issue73/chung.html)
