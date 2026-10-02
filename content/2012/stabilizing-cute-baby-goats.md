---
date: '2012-02-28'
title: Stabilizing Cute Baby Goats
category: English
tags: Canon EOS 7D, Linux, stabilization, transcode, Video
---

![Newborn kid still wet from birth, peering out from a bed of straw beside a wooden post](newborn-kids-baby-goats-preview.jpg)

## Stabilizing WHAT?!?

Baby goats. Cute baby goats. Yes, you're reading it right. Look:

https://www.youtube.com/watch?v=el6VMY8KZHo

Yeah, I know, this is a naive video that belongs to [/r/aww](https://www.reddit.com/r/aww/). But any excuse is good to me when its all about playing with video.

These kids (as baby goats are called) decided to come to this world the night I was around. In a hurry I grabbed my Canon 7D and filmed these newborns with a Sigma 30mm f/1.4 EX DC HSM to leverage its large aperture. And as expected, in the night, with no artificial light and no extra stabilization device, the resulting footage are extremely shaky.

I tried to stabilize the shots but was really disappointed by the results. The final version of the video you watched above only feature the original footage, without any stabilization. But for posterity, here are some notes about the tools I played with.

## vid.stab

![Raked photo of a screen scrolling the transcode stabilize log, listing the shakiness, accuracy, stepsize and mincontrast settings](transcode-stabilizer-log.jpg)

The first tool I tried was [vid.stab](https://public.hronopik.de/vid.stab/), a Transcode plugin that is now part of Transcode itself. But the 1.1.5 version that is bundled with the current Ubuntu 11.10 is quite old.

I wanted to compile it from its [sources](https://github.com/georgmartius/vid.stab). But the [binary distribution](https://public.hronopik.de/vid.stab/download.php) available on the project website works out of the box. To save some effort, let's install the latter:

```shell-session
$ wget https://public.hronopik.de/vid.stab/files/vid.stab-0.93-transcode-1.1-binary-x86_64.tgz
$ tar xvzf ./vid.stab-0.93-transcode-1.1-binary-x86_64.tgz
$ sudo mv ./vid.stab-0.93-transcode-1.1-binary-x84_64/filter_*.so /usr/lib/transcode/
$ rm -rf ./vid.stab-0.93-transcode-1.1-binary-x8*
```

Now, as explained in the [documentation](https://public.hronopik.de/vid.stab/features.php), you have to let transcode analyze the video:

```shell-session
$ transcode -J stabilize -i ./MVI_1714.MOV -y null,null -o dummy
```

Only after this first pass you can apply the stabilizing transformations:

```shell-session
$ transcode -J transform -i ./MVI_1714.MOV -y ffmpeg -F huffyuv -o ./MVI_1714-stabilized.MOV
```

If your not satisfied with the result, you can increase the area of tracking points with the `shakiness` parameter:

```shell-session
$ transcode -J stabilize=shakiness=8:show=1,preview -i ./MVI_1714.MOV -y null,null -o dummy
```

In the command line above we added the `show=1,preview` parameters, which have the nice effect of displaying a preview of the work done behind the scene:

![Debug view of the stabiliser at work, six dark measurement fields overlaid on the kid, each with its tracked point marked at the centre](goat-tracking.jpg)

And if you want to see the transformations applied in the final video, just deactivate the cropping and zooming mechanism:

```shell-session
$ transcode -J transform=crop=1:optzoom=0 -i ./MVI_1714.MOV -y ffmpeg -F huffyuv -o ./MVI_1714-stabilized.MOV
```

Finally, here are some command helpers to automate the stabilization process for a massive amount of video:

```shell-session
$ find ./ -name "*.MOV" -exec transcode -J stabilize -i "{}" -y null,null -o dummy \;
$ find ./ -name "*.MOV" -exec transcode -J transform -i "{}" -y ffmpeg -F huffyuv -o "{}.stabilized.avi" \;
```

## Alternative tools

I told you I was disappointed by the results. For example, in the first shot of the video above, `vid.stab` will stabilize based on the movements of the head of the goat, not based on the background. All of this because tracking points are generated on high-contrast area. Unfortunately in this first scene, the only high contrast area is the kid's head.

Even in shots where the contrast is in our favor, software stabilization don't always produce nice output. If by chance the tracking points are set on the right objects (those that should be considered motionless), the results may not be pleasing, as it may expose inappropriate skewed perspective, shifting motion-blur and spacial deformation.

While a little bit smarter, [YouTube's embedded stabilization effect](https://youtube-global.blogspot.com/2011/03/lights-camera-edit-new-features-for.html) still suffer from these same short-comings. If it tries to smooth out consecutive transformations better than `vid.stab`, it still fails to produce nice output devoid of unattractive artifacts.

Another tool worth trying is [VirtualDub](https://www.virtualdub.org), which you can run under [Wine](https://www.winehq.org) and leverage its [deshaker plugin](https://www.guthspot.se/video/deshaker.htm). But I didn't tested it.

Last but not least, [Blender can be used to stabilize videos](https://www.youtube.com/watch?v=OJujeSQctEk). Again I haven't tried this yet, but I think it's the best investment of you time, since the new tracking features make Blender a powerful tool for 3D integration.

## Conclusion (tl;dr)

There is no silver bullet: don't expect software stabilizer to save your shaky shots in post-production. If you want steady shots, plan them beforehand and use proper gear on site, be it a monopod, a tripod, a slider, a dolly, a crane or a steadicam. That's the only way to eliminate the pain and deception when you hit the editing room.
