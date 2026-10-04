---
date: '2020-10-12'
title: 'Billing pipeline: a critical time sensitive system'
category: English
tags: Python, billing, payment, scaleway, unittest, software engineering, quality assurance, management, pipeline, data, money, business, AWS, lambda, date, time, falsehood, Chesterton's fence, arrow, TrueTime, google, pytest, meta-package-manage, mail-deduplicate
---

This is an answer to [Antoine Veuiller](https://www.linkedin.com/in/antoine-veuiller/)'s article, an [Introduction to Flaky Tests by Example](https://medium.com/@aveuiller/stories-of-flaky-test-encounters-in-the-wild-a152bf7151f5), in which he shares his experience on tackling unstable tests.

And I'm the author of the flaky tests he's talking about! 😬

## Story time!

I started designing and implementing Scaleway's billing pipeline in 2013. This was to be a critical system, given its purpose, collecting money. It was very seriouz bizzness.

![Now remember, kids, the internet is serious business -- Isaac Asimov](internet-is-serious-business.jpeg)

I was worried a lot about both accuracy and precision of the numbers it produced. Strange how things gets real when you add a dollar sign. 🤑

My system had to **track nano-euros at the milli-seconds time granularity**. Why? Read the [pricing page of AWS Lambda](https://aws.amazon.com/lambda/pricing/). They're billed 100ms usage at a time. Here lies my MVP: to be able to invoice usage-based cloud computing resources.

So I wrote extensive unit tests to prove that I knew how to add, subtract and multiply.

![Math is Math!](math-is-math.jpeg)

Well, to be picky, it was more an acceptance suite than proper unit-tests. Whatever.

Fast forward 4 years, Scaleway is bigger, and millions of euros are collected by the dual billing & payment stacks. 📈 I'm [no longer an engineer, but the manager]({filename}/2020/engineering-to-management-transition.md) of the team taking care of the system. 👔

I hired Antoine. And there he was, fixing the crap I implemented 7 years ago. Not only did he fix the tests nobody had time to work on, but he uncovered more edge-cases and wrote an entire article about it. 😍

Thanks a lot Antoine for taking the resolution and effort to fix my old mess! 😁 And I'm sure the definitive absence of flaky tests reduced the overall stress of the team.

Now [go read that stuff](https://medium.com/@aveuiller/stories-of-flaky-test-encounters-in-the-wild-a152bf7151f5): it demonstrates how hard it is to reason with bare temporal logic, even for seasoned engineers. On my side, practicing this made me compile that [awesome list of falsehoods programmers believe in](https://github.com/kdeldycke/awesome-falsehood), as a cautionary tale of all things that might go wrong.

Let's continue with some complementary notes to provide context on the system.

## Ignoring flaky tests

When I was alone behind the billing pipeline, I quickly refrained from pushing code in production during the first few days of each month. That was based on the traumatic (but enlighting) early days of operating a live cloud computing platform. With real customers on the other side of the API.

This dogma was carried on when I [grew the team from 0 to 12 engineers]({filename}/2020/engineering-to-management-transition.md). Even though I repeated ad-nauseum the context of that decision, I feared it might have been lost in a typical case of [Chesterton's fence](https://en.wikipedia.org/wiki/Wikipedia:Chesterton%27s_fence). So here it is, in written form.

The main reason was the massive reports being produced in that critical time-window. The consolidation of accounting and financial numbers of our holding company was, among other things, dependent on these reports. The blast radius of our team was suddenly inflated, at the billion-dollar level. 😅

Hence the compromise. In the grand scheme of things, we had to reach operational excellence before taking care of our flaky tests. And I'm proud to highlight that under my watch, the team always delivered on schedule. Because the *money must flow*.

![The Spice must flow](the-spice-must-flow-cat-version.jpg)

As a manager, **I'm the only one responsible** for allowing the team to disregard these technical issues.

## Time arithmetics

> Once again, and unfortunately for us, the project was using [`arrow`](https://github.com/arrow-py/arrow)

The reason I choose `arrow` at the time was practical. It was the only Python library actively maintained that was providing [date-aware ceiling and flooring methods](https://arrow.readthedocs.io/en/stable/guide.html#ranges-spans). I wouldn't have been able to tame the side-effects of quantization without those.

## Time reference

> Fortunately, and thanks to some previously well-thought environment on the project, we had a central method to provide the current date, which was initially intended to prevent the use of a wrong timezone.

Thanks for the kind words! That was one of the tiny design decision I made in the first few weeks of the project. I came up with that central hook as a place from where to fetch a solid time reference. If it ended up enforcing good usage of timezones, the original intent was more convoluted.

I was building a system in a domain for which transactions were basically invented. Try for instance explaining to customers that their credit cards got charged twice because of eventual consistency...

Scaleway's ambition was to have datacenters all over the world (that's the reason I signed in). So how the codebase would behave in a massively distributed architecture? Time at that scale is hard. And it was at the root of everything, so I created that unique entry point to fetch a reliable timestamp.

It was supposed to be a gateway to the local datacenter's GPS source, or a fancy atomic clock. I even fantasized having access to [TrueTime](https://cloud.google.com/spanner/docs/true-time-external-consistency)-like protocols (not even sure we even needed it). BTW, did you know [Google's TrueTime is staffed by 16 senior SREs](https://twitter.com/kdeldycke/status/1102172902995173376), which "*had take measures up to and including calling the USAF and telling them their satellites are fucked up*"?

## Busting coupling

> By “chance” the tests were always run in the right order for years. This situation could have been detected way earlier by using a random execution order for tests. It happens that python has simple modules to do so.

Great minds think alike! I switched over [`pytest`](https://docs.pytest.org) in my pet projects (namely [`meta-package-manager`](https://github.com/kdeldycke/meta-package-manager) and [`mail-deduplicate`](https://github.com/kdeldycke/mail-deduplicate)) and used [`pytest-randomly`](https://pypi.org/project/pytest-randomly/) too to great success.

BTW, `pytest` is powerful, but feels magical at times. I spent more time working on it than I anticipated, so a switch to `pytest` should be seen as an investment to increase the quality of your software.

## Randomize all the things!

> ### A good flakiness
>
> (...) the test was generating numerous instances of the class with randomized inputs.

That good flakiness has a name: [fuzzing](https://en.wikipedia.org/wiki/Fuzzing)! 😉

[![Dilbert's random number generator](https://assets.amuniversal.com/321a39e06d6401301d80001dd8b71c47)](https://web.archive.org/web/20201012020052/https://dilbert.com/strip/2001-10-25)
