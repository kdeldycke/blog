---
date: '2010-10-15'
title: Export Quartz Composer to video
category: English
tags: Animation, Apple, Kaleidoscope, MacBook, Quartz Composer, Video, Visual, Mac OS X 10.6 Snow Leopard
---

[Quartz Composer](https://en.wikipedia.org/wiki/Quartz_Composer) is a really
nice piece of software for visualists. It
allows you to create animated and/or interactive compositions mixing sounds,
images, effects, user inputs and any other kind of data. In fact, Quartz
Composer was the main reason I bought a MacBook Pro 18 months ago.

The first composition I created was this simple kaleidoscopic effect with
shifting colors:

https://www.youtube.com/watch?v=a7YNLp7xy8k

The [source composition
]({attach}kaleidoscope-000.qtz) is available under
a [Creative Commons 3.0 BY-SA license
](https://creativecommons.org/licenses/by-sa/3.0/). And here is the screenshot
of the main patch:

![Quartz Composer root patch wiring a Star Shine through an Image Crop into a Psychedelic patch, with a Color Wheel macro and an LFO feeding its colour and speed inputs](kaleidoscope-000-main-patch.png)

And this is how I designed the color wheel sub-patch:

![Inside the Color Wheel macro: the cycle period fanned through three multipliers into three LFOs, one per channel of an RGB Color patch](kaleidoscope-000-color-wheel-macro-patch.png)

If creating a composition is really simple and straightforward, exporting the
result to a video file is another story...

I first tried the [Export to Movie](https://quartzcomposer.com/plugins/1-export-to-movie) v1.3b plugin. But it didn't worked on my Mac OS X Snow Leopard, throwing me this exception every time:

![Quartz Composer internal error dialog reporting that NSDate timeIntervalSinceReferenceDate was sent to an uninitialized date object, over a long stack trace](quartz-composer-export-to-movie-exception.png)

```text
0x8272938b: -[QCContext renderPatch:time:arguments:]
0x8272906d: -[QCGraphicsContext renderPatch:time:arguments:]
0x827281bb: -[QCOpenGLContext renderPatch:time:arguments:]
0x0000d873
0x8276495b: -[QCView render:arguments:]
0x82763f68: -[QCView startRendering:]
0x0000cd80
0x8548584e: _nsnote_callback
0x81ccda90: __CFXNotificationPost
0x81cba008: _CFXNotificationPostNotification
0x8547c7b8: -[NSNotificationCenter postNotificationName:object:userInfo:]
0x86da2f5f: -[NSWindow _reallyDoOrderWindow:relativeTo:findKey:forCounter:force:isModal:]
0x86da2bbe: -[NSWindow orderWindow:relativeTo:]
0x86da0544: -[NSWindow makeKeyAndOrderFront:]
0x86fa55c1: -[NSWindowController showWindow:]
0x0000ca7f
0x873461d3: -[NSToolbarButton sendAction:to:]
0x86fb73c1: -[NSToolbarItemViewer mouseDown:]
0x86ea4763: -[NSWindow sendEvent:]
0x86dd9ee2: -[NSApplication sendEvent:]
0x0000a994
0x86d70922: -[NSApplication run]
0x00001d2b
```

So I tried the old trick of [importing compositions in iMovie](https://web.archive.org/web/20101008045750/http://blogs.ipona.com/james/archive/2005/05/05/1040.aspx). If this was possible in the past with iMovie '06, Apple removed this feature in iMovie '09 (`https://www.quartzcompositions.com/phpBB2/viewtopic.php?t=594`).

My last chance was another plugin: [Movie Exporter
](https://quartzcomposer.com/plugins/6-movie-exporter) (`v0.0.20091011`). As the
other one, you have to drop your original composition in a _Render in Image_
macro block and export the resulting stream to the _Movie Exporter_ block:

![Patch rewired so Render in Image feeds a virtual splitter that drives both a Movie Exporter and a Billboard, the inspector set to render 1280 by 720](movie-exporter-patch.png)

It did the trick but it looked like I messed things up: my goal was to export a
720p clip. But compression artifacts are so present in the final video that I
think the exported images are blow-ups of a rendering executed at a much lower
resolution. The rendering in the preview panel support this hypothesis:

![Quartz Composer viewer running the composition at 60 fps, showing two green light beams meeting in a bow-tie against black](kaleidoscope-viewer.png)

Another big problem with this video export lies in the framerate: it cannot be
set. For this composition the plugin exported a clip at 11fps. Which is far
from fluid. I guess it's because of the plugin grabbing images in real-time
instead of taking the necessary time to render them one by one.

At the end, because of the reduced number of options available to export QC's
compositions to movies, and because of the proprietary nature of the platform,
I don't want to invest more time and energy in Quartz Composer.

I did some more experiments with it last year. I plan to share them with you
and published them in the coming weeks. Then I'll be free to sell my Apple
machine and switch back to a full Open-Source stack (I'm thinking of
[Processing](https://processing.org),
[PureData](https://en.wikipedia.org/wiki/Pure_Data) and their derivates here).
