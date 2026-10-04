---
date: '2011-07-12'
title: Making of Omashay's *Wish You Looked at Me* music video
category: English
tags: 1080p, 720p, Cool Cavemen, Kdenlive, Linux, Music, music video, omashay, Video, youtube
---

![Four-way split screen of the finished video: hands on a piano keyboard, a red bass being played, a drummer behind his kit, and the singer at a pop shield in headphones](omashay-wish-you-looked-at-me-preview.png)

Last month I edited the [Wish You Looked at Me video clip
](https://omashay.com/wish-you-looked-at-me-video-clip/) for the [Omashay
project](https://omashay.com). This is a side-project of [Cool Cavemen's
saxophonist](https://coolcavemen.com/biography/tomasito/). The video is finally
available on YouTube:

https://www.youtube.com/watch?v=iHi0lwhTqqc

All the video material was shot by Tomasito itself, with his Canon PowerShot SX200IS point-and-shoot camera. This camera produce 30fps 720p clips.

He came to me with all these `.mov` files, and the idea of combining them into
a classical split-screen layout. He had no idea how to do this, so I accepted
to help him with my technical knowledge.

I fired up my Kdenlive (v0.8 on Kubuntu 11.04) and in a matter of hours, the
project was done. With source videos of 720p, I naturally chose 1080p as the
final resolution. I kept the 30fps framerate to not alter the original time
resolution.

The most boring part of the edit was the first step, in which we synced all
clips together with the reference audio track. Here is how the timeline looked,
with one track for each instrument:

![Kdenlive with every instrument on its own track, thirteen long clips stacked above the reference audio, all waveform-aligned](wish-you-looked-at-me-kdenlive-timeline-01.png)

We had to work around some annoying Kdenlive bugs, as it had some problems
handling so much tracks in parallel. Fortunately these bugs were fixed in a
matter of days with a new build of MLT.

Next step was to mark out the structure of the song. Tomasito placed blue
markers along the timeline, and we cut all tracks following that structure. It
resulted in a matrix of clips:

![The same timeline after cutting to the song structure, blue markers labelling intro, verses, choruses and bridge, leaving a dense matrix of short clips](wish-you-looked-at-me-kdenlive-timeline-02.png)

Then for each segment, we choose the 4 clips that we wanted to show and deleted
the others:

![The matrix thinned out to four clips per segment, leaving gaps where the unused takes were deleted](wish-you-looked-at-me-kdenlive-timeline-04.png)

Then I created 4 special tracks to which I applied a global positioning and
scaling effect, to have each track fill one corner of the screen. We moved
there all the clips we selected in the previous step, and cleaned up the
timeline a bit:

![Timeline reduced to four corner tracks, the effects panel showing the pan and zoom set to 50 percent to park one clip in a quadrant](wish-you-looked-at-me-kdenlive-timeline-05.png)

At this stage the project was mostly done. It was just a matter of adding
intro, outro and fade in/out to obtain our final video:

![Finished project with a titling track added, the monitor showing the guitarist beside the Wish You Looked at Me title card](wish-you-looked-at-me-kdenlive-timeline-06.png)

Tomasito basically did the whole editing of the project. And I have some
evidences:

![Tomasito editing in a darkened room, laptop under his hands and the Kdenlive timeline up on the big monitor, between studio speakers](tomasito-editing-session.jpg)

I just showed him how to manipulate Kdenlive timelines, and cut/move/paste
clips, and he was absolutely autonomous in a matter of minutes. I just did the
transitions, the title cards integration and the screen splitting. I'm not sure
I deserve the title of editor for this project, but he still insisted to add me
in the credits... :)

Of course split-screen is [far from new
](https://web.archive.org/web/20111027125743/http://monsterkidclassichorrorforum.yuku.com/reply/304973/Oldest-Split-Screen-effect)
and [was done](https://www.youtube.com/watch?v=vsMIuuV05uc) [a million times
before
](https://en.wikipedia.org/wiki/Split_screen_effect#Notable_uses_of_split_screen).
But it's a simple yet effective concept that require absolutely no investment
(apart time). This also gave me the opportunity to play again with Kdenlive and
assess its user-friendliness and edit capabilities on a real project. But at
the end, it was just a great excuse to work with a friend on a little video
project! :)
