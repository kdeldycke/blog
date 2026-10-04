---
date: '2013-03-26'
title: 'Tale of Two: production notes'
category: English
tags: Kdenlive, Linux, Omashay, timelapse, slow-motion, slowmoVideo, imagemagick, transcode, vid.stab, Blender
---

![Finished timelapse frame: a large oil portrait of a face with a hand pressed to the cheek, propped on an easel in a bedroom, the sides feathered away by the paint-stroke mask](tale-of-two-preview.jpg)

This is the fourth video I've work on for [Omashay](https://omashay.com):

https://www.youtube.com/watch?v=4HtfugU_mGg

This video is a timelapse of a painting Tomasito made in 2007. It's based on a series of photos he took every 10 minutes:

![Contact sheet of about seventy numbered photos of the easel, the canvas going from blank white through ochre outlines to the finished portrait](tale-of-two-timelapse.png)

## slowmoVideo

I tried to produce a timelapse out of these images a year ago. In fact, that was the original project I was referring to in my [previous article]({filename}/2013/goodnight-video.md), the project which triggered my initial interest into [slowmoVideo](https://github.com/slowmoVideo/slowmoVideo).

But the experiment failed and I abandoned this endeavor. Instead of slow-motion, and because of the low timing resolution of the photos, I assumed a simple slideshow would do it.

## Blender

The original photos were not consistent. To make them work as a slideshow, they required some stabilization. I tried the new [tracking features of Blender](https://web.archive.org/web/20130420171725/http://wiki.blender.org/index.php/Doc:2.6/Manual/Motion_Tracking):

![Blender motion tracking on the slideshow, tracker crosses scattered over the canvas and the room, with the 2D stabilization panel and its track list open on the right](blender-timlapse-stabilization.jpg)

While I could feel the power of the tracking tools, my limited knowledge of Blender stopped me. I abandoned this approach. But one day for sure, I'll give Blender the time it deserves.

## vid.stab & Kdenlive

My plan B for stabilization was [Transcode's vid.stab plugin]({filename}/2012/stabilizing-cute-baby-goats.md).

But it can't read images: it only takes videos for input. So we'll produce a video file of a simple slideshow in Kdenlive, then feed the result to vid.stab.

First, in a separate project, I created a stupid slideshow of 1 photo per frame, without any transition:

![Kdenlive slideshow clip properties set to one frame per image with no dissolve or animation, reporting 70 images found](redux-generation.png)

To keep details, I exported the project to a high-quality h264 stream composed of I-frames only:

![Kdenlive render dialog on the Lossless/HQ destination with the H.264 I-frame only profile selected](export.png)

I wanted to use a true lossless codec here, but after several trials and errors, this profile was the only one <code>vid.stab</code> was able to digest.

I can now apply the stabilization, with a high shakiness parameter to make the algorithm ignore the lack of fluidity:

```shell-session
$ transcode -J stabilize -i ./slideshow-redux.mp4 -y null,null -o dummy
$ transcode -J stabilize=shakiness=8 -i ./slideshow-redux.mp4 -y ffmpeg -F huffyuv -o ./slideshow-redux-stabilized.avi
```

Then we extract all frames of the stabilized video to get a new set of photos:

```shell-session
$ mkdir ./timelapse-stabilized
$ cd ./timelapse-stabilized
$ cp ../slideshow-redux-stabilized.avi
$ ffmpeg -i ./slideshow-redux-stabilized.avi -f image2 stab%05d.png
```

From the produced images, I created a new slideshow with proper transitions.

I presented the final rendering to Tomasito, and we agreed that the result, while not incredible, was a good excuse to distribute one of his song on YouTube.

He planned to published the video, but the final editing step was postponed by several months. And then we both forgot the project.

## slowmoVideo, again

Until last January when, after [some efforts]({filename}/2013/slowmo-video-ubuntu-12-10.md), I managed to [produce something with slowmoVideo]({filename}/2013/goodnight-video.md). We resurrected the project.

I applied the raw slowmoVideo transformation on the initial set of photos. And the result was good enough. But Tomasito wanted more, and stabilized all the 70 images of the original set by hand!

After this herculean task, I cropped & resized the images to fit the 1080p resolution:

```shell-session
$ convert -resize 1920x1080 -background black -gravity center -extent 1920x1080 ./manually-stab-keyframes/* pict%04d.png
```

[As for Goodnight]({filename}/2013/goodnight-video.md), we tried to get rid of the wide black bars on the sides. [QPX](https://web.archive.org/web/20120806035017/http://wqpx.wordpress.com/) created for us a mask made of paint strokes:

![Black and white mask, a white centre with ragged paint-stroke edges eating into the black bars down either side](video-mask.png)

Then I used that mask to blend the photos with a background fiber texture from [Subtle Patterns](https://subtlepatterns.com):

```shell-session
$ find ./ -iname "pict*.png" -exec composite "{}" ./stressed_linen-1080p.png ./Masque-02.png "{}"-composed.png \;
```

Finally I send these pre-rendered keyframes to slowmoVideo to produce a 4 minutes ultra-slow-motion. Then Tomasito added a title and credits.

There is no magic and the final result could have been better if properly shot. What's missing was a steady canvas and good camera positioning, and of course a lower delay between photos. These are the perfect conditions to produce a proper timelapse, and I'm sure we'll demonstrate that in a future project.
