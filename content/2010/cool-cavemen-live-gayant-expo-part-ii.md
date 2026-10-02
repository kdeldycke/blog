---
date: '2010-02-20'
title: Cool Cavemen live at Gayant Expo, part II.
category: English
tags: 720p, Cool Cavemen, Deinterlacing, douai, gayant expo, Image processing, MPEG-2, Pixel aspect ratio, Video
---

Here is "Funky Cops", the second Cool Cavemen's live song at Gayant Expo:

https://www.youtube.com/watch?v=3sI35h0t4-8

I [released this video two weeks ago](https://coolcavemen.com/2010/video-funky-cops-live-gayant-expo/) for Cool Cavemen. As I try to release one video every week, I give a high priority to the editing work. This leaves me with little time to write on this blog.

But starting from now, I plan to publish a blog post for each video. I'll use these articles to write about one aspect of the work involved behind the scene.

In the [first post of the series]({filename}/2010/cool-cavemen-live-gayant-expo-first-video-released.md), I gave you the context in which the concert was performed. Today the post is dedicated to video formats. First, let's talk about the video sources...

The concert was shot with 4 cameras. Among them, only two were of the same kinds. Those were part of the live broadcasting system of the event. This explain the "[mise en abyme](https://en.wikipedia.org/wiki/Mise_en_abyme)" effect in the background screen:

![Concert frame captioned Funky Cops, the singer up on a monitor wedge with guitarist and bassist behind him, and the same footage projected on the wall above the stage](funky-cops-mise-en-abyme.png)

At the end of the gig, I wasn't be able to retrieve two continuous feeds. Instead I got an already-edited video corresponding to what was projected live (*sigh*).

As a result, I ended with 3 video sources:

1. A DVD-like video stream ([576i](https://en.wikipedia.org/wiki/576i)) produced by my consumer-grade camera ([now for sale at 0.01€ on ebay](https://twitter.com/kdeldycke/status/9299604161)). It produces 720x576 pixels [interlaced frames](https://en.wikipedia.org/wiki/Interlace) at 25 fps, with a [pixel ratio](https://en.wikipedia.org/wiki/Pixel_aspect_ratio) of 16:15 (giving 768x576 pixels frames at 1:1) and a final [display ratio](https://en.wikipedia.org/wiki/Display_aspect_ratio) of 4:3. All encoded as a 9 Mbps MPEG-2 stream in a MPEG-PS container.

2. A [720p](https://en.wikipedia.org/wiki/720p) video stream: 1280x720 pixels progressive frames at 30 fps, with 1:1 pixel ratio and 16:9 display ratio, encoded as variable bitrate MJPEG stream in a QuickTime container.

3. The already-edited video stream ([Half-D1](https://www.videohelp.com/glossary?H#Half%20D1)) from unidentified Sony cameras: 352x576 pixels interlaced frames at 25 fps, with a pixel ratio of 24:11 (giving 768x576 pixels frames at 1:1) and a final display ratio of 4:3. The file was a 6 Mbps MPEG-2 stream in a MPEG-PS container.

All those information were extracted thanks to `ffmeg`, `mplayer` and `tcprobe` (see [all the command lines involved]({filename}/2006/video-commands.md)).

As you can see, this is an absolute mess! There is no consistency! And now, before starting the video editing itself, I have this important decision to make: choose the final video format, in which my project will be rendered.

Let me explain how I did it. But before, I have to tell you something. To me, an interlaced video at 25 fps is just a 50 fps stream with half the vertical resolution. This is important for you to know if you want to understand how I perceive quality. I'll probably explain it in details in a future article. But for now, this should give you enough insights on how I came up with my two strategies.

The first one is the "maximizing" strategy. It consists of keeping the best parts from all video sources. Based on formats described above, this means 1280x720 pixels progressive frames at 50 fps, with 1:1 pixel ratio and 16:9 display ratio. In this process we create non-existent information by scaling and interpolating spatial and temporal data.

The second strategy is the "minimizing" strategy which, you can guess from its name, is the exact opposite of the first one. Here we discard spatial and temporal information until we reach a sub-format shared by all sources. In our example, this gives 352x288 pixels frames at 30 fps, with a pixel ratio of 24:22 and a display ratio of 4:3. There, 288 is half 576, which is the result of using a [deinterlacing "bob" filter](https://en.wikipedia.org/wiki/Deinterlacing#Field_Extension_Deinterlacing) on video streams #1 and #3 to get 50 fps. And for the pixel ratio, as we "bobbed" the interlaced videos, we keep the worst horizontal scaling and multiply the vertical scaling by two, which give us 24:22.

For this project, I finally went by the first strategy. I chose to render the project to a 720p video at 25 fps, with a 1:1 pixel ratio and 16:9 display ratio. Also known as... [HD-Ready](https://en.wikipedia.org/wiki/Hd_ready)!

Why this format? It's the most popular one that closely match the characteristics we established three paragraphs above. It's also quite standard, and "gives a chance" to the second video source to display in full resolution. I also felt that it will cause less pain when confronted to the wide range of software video players out there.

Now that I have decided which format to use, I can create a project in my video editor with the right parameters and start the editing process. But this is another topic for another post!
