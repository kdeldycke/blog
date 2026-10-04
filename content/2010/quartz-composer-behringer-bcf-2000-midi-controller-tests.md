---
date: '2010-12-14'
title: Quartz Composer & Behringer BCF-2000 MIDI controller tests
category: English
tags: Animation, Apple, Berhinger, Canon EOS 7D, Creative Commons, Jamendo, Kdenlive, MacBook, MacBook, midi, MIDI-controlled graphics, Quartz Composer, tokina, USB, Video, Visual
---

A year ago I explored visual control by plugging a generic Behringer BCF2000 MIDI controller in Apple's [Quartz Composer](https://en.wikipedia.org/wiki/Quartz_Composer). My initial intention was to drive some animations and visuals during [Cool Cavemen](https://coolcavemen.com)'s live concerts. Now that's I've abandoned the idea of using Quartz Composer, it's time to share these stuff with you.

So here is my MIDI playground:

![Quartz Composer patch combining a MIDI controllers receiver and an audio input, routed through pulse patches and a pulse chooser into the colour and geometry of a sprite](quartz-composer-midi-playground.png)

Nothing exceptional to see here. It's just a bunch of dumb patches to control the color of the background screen and its intensity. The latter can be modulated by pulses with different profiles, and also by the sound captured by the MacBook's microphone. The [source composition is downloadable]({attach}midi-controlled-playground.qtz).

Just for the sake of it, I've recorded a quick and dirty demo with my Canon 7D (set to 1080p, 25 fps and 1/50 shutter speed) and the fantastic Tokina 11-16mm f/2.8:

![Filming setup at home: the EOS 7D on a tripod aimed down at a glass table holding an open MacBook Pro and the Behringer control surface, red sofa behind](behind-the-scene-of-bcf2000-and-quartz-composer-video.jpg)

Here is the video, which I edited with [Kdenlive](https://www.kdenlive.org):

https://www.youtube.com/watch?v=I8JN40Vq_do

The audio is sourced from [Jamendo](https://jamendo.com). It's the track [One Year](https://web.archive.org/web/20111215214618/http://www.jamendo.com/en/track/556566) written by [Paolo Lunardi](https://web.archive.org/web/20100831043155/http://www.jamendo.com/en/artist/Paolo_Lunardi) for his album [Essential](https://web.archive.org/web/20110113150924/http://www.jamendo.com/en/album/64689), and released under a [Creative Common BY-SA v3.0 license](https://creativecommons.org/licenses/by-sa/3.0/) (thus making my video subject to the same license).
