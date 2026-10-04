---
date: '2013-07-07'
title: Compile BFGMiner for scrypt-based CPU mining
category: English
tags: scrypt, CPU, Linux, BFGMiner, crypto-currency, Bitcoin, Litecoin, Kubuntu 13.04
---

I wanted to try
[mining](https://en.wikipedia.org/wiki/Bitcoin_protocol#Mining) on my
Kubuntu 13.04. Not to get rich, but simply to verify that the production of
[crypto-currencies](https://en.wikipedia.org/wiki/Cryptocurrency) really was
decentralized, and also to learn how-to mine.

I first tried mining [Bitcoin](https://bitcoin.org) with
[BFGMiner](https://web.archive.org/web/20130502101446/http://bfgminer.org/). I choose the later over
[cgminer](https://github.com/ckolivas/cgminer) because that's the only one I
found to be readily [available from an Ubuntu
PPA](https://launchpad.net/~unit3/+archive/bfgminer):

```shell-session
$ sudo tee -a /etc/apt/sources.list <<-EOF
    deb https://ppa.launchpad.net/unit3/bfgminer/ubuntu quantal main
    deb-src https://ppa.launchpad.net/unit3/bfgminer/ubuntu quantal main
  EOF
$ sudo aptitude install bfgminer
```

Unfortunately the version was not up to date, and was not compiled for mining
[scrypt](https://en.wikipedia.org/wiki/Scrypt)-based coins like
[Litecoin](https://litecoin.org). Here is how I built BFGMiner with this
support.

Install the dependencies:

```shell-session
$ sudo aptitude install build-essential autoconf libtool libjansson-dev libcurl4-gnutls-dev libncurses5-dev libudev-dev libusb-1.0-0-dev yasm uthash-dev
```

Get a copy of the latest version and prepare the environment:

```shell-session
$ cd ~
$ git clone https://github.com/luke-jr/bfgminer.git
$ cd bfgminer/
$ ./autogen.sh
```

Then I built it while enabling scrypt and CPU optimizations:

```shell-session
$ ./configure --enable-cpumining --enable-scrypt
$ make
```

Then create a config file in `~/.bfgminer/bfgminer.conf`:

```json
{
  "pools": [
    {
      "url": "stratum+tcp://coinotron.com:3334",
      "user": "foo.ltc",
      "pass": "xxxxxxxxxx",
      "pool-priority": "0"
    },
    {
      "url": "https://p2pool.org:9327",
      "user": "LTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "pass": "password",
      "pool-priority": "1"
    }
  ],
  "algo": "scrypt",
  "api-port": "4028",
  "expiry": "120",
  "expiry-lp": "3600",
  "gpu-dyninterval": "7",
  "log": "5",
  "no-pool-disable": true,
  "no-show-processors": true,
  "no-show-procs": true,
  "queue": "1",
  "scan-time": "60",
  "scrypt": true,
  "skip-security-checks": "0",
  "submit-stale": true,
  "temp-hysteresis": "3",
  "shares": "0",
  "kernel-path": "/usr/local/bin"
}
```

And your ready to launch the miner:

```shell-session
$ ~/bfgminer/bfgminer
```
