---
date: '2010-05-12'
title: Lotus Notes' Rich Text to MIME conversion error
category: English
tags: email, Gimp, Lotus Notes, MIME
---

Today I encountered a strange error while using Lotus Notes. I had a "_Cannot convert Notes Rich Text message to MIME message_" error:

![Alert reading: cannot convert Notes Rich Text message to MIME message](notes-rich-text-to-mime-conversion-error.png)

This was triggered when I tried to move certain mails from one account to another. And to add insult to injury, this nasty and dangerous error will make you loose data.

Let's say you want to cut and paste a batch of 10 mails. Then that error occurs while Notes paste the 3rd message. It means you'll loose the last 7 messages of your batch. Why? The 10 messages will be removed from their original location on cutting, and the last 7 messages will be trapped in the copy buffer. Isn't that a reasonable reason to [hate Lotus Notes](https://www.codinghorror.com/blog/2006/02/lotus-notes-survival-of-the-unfittest.html)?

Anyway. After several tests and experiments, I finally found the common property shared by all those reluctant messages. They all have inline images embedded in the body of the mail, like the one below:

![Notes message with its text blurred, two inline images ringed in hand-drawn red and arrowed, each collapsed to a thin ruler strip](inline-images-in-lotus-notes-mail.png)

In mail edit mode, you can get properties of these objects and get confirmation that they are inline images:

![Right-click menu open on Picture Properties beside the picture inspector, its source given as in-line image with scaling at 100 percent](lotus-notes-inline-picture-properties.png)

As you can see above, the edit mode lets you manipulate (cut, copy, paste, ...) these embedded pictures. Let's take advantage of this to fix our initial issue.

Here is my procedure to make these mails pass through the conversion error:

1. In Notes' edit mode, cut all inline pictures, one picture at a time;

2. For each cut picture, paste it as a new image in the image editor of your choice ([Gimp](https://www.gimp.org) did the trick for me);

3. Save each image on your local disk;

4. Now that all inline images are removed from the original mail, attach (but don't paste) to it all the images you saved in the previous step;

5. Finally, save mail modifications in Notes and you'll be able to move the mail without the conversion error.

This is really dirty, and isn't bearable past a few mails. But that's the only solution I found so far. Of course if you have a superior/automated way to address this lame bug, I'll be happy to hear that! :)

## Update (Dec. 2010)

I [recently tried again to migrate mails]({filename}/2010/ultimate-guide-lotus-notes-mail-migration.md#method-5-lotus-notes-client-on-windows-xp) with embedded images, but this time with Lotus Notes 8.5.2 on Windows XP (inside a Qemu instance).

Interestingly, embedded images didn't triggered the _Rich Text to MIME conversion_ error. Instead, inline images were automatically replaced by a generic text in the body of the mail, and the binary payload was moved as an attachment.

You can see this behavior in one of the mail I imported directly from Notes to Gmail:

![The same message once imported into Gmail, the inline pictures replaced by embedded image moved to file notices and two small GIF attachments](lotus-notes-imported-mail-in-gmail.png)

This is much more acceptable...
