---
date: '2020-06-12'
title: 10G Network at Home
category: English
tags: hardware, network, 10G, freebox, NIC, switch
---

Into my [journey building a NAS for the home office]({filename}/2020/nas-hardware.md), I went down the rabbit hole and chased better file transfer performance. The next step would be a network upgrade. And so I started exploring 10G at home. It is fancy, but doable.

## Internet access

I'm already equipped with a [Freebox Delta Server](https://www.systemplus.fr/wp-content/uploads/2019/08/SP19459_Freebox-Delta-Server_system_plus_consulting_sample.pdf) with 10 Gbps fiber downlink, 600 Mbps uplink. We can plan a multi-step upgrade.

## NAS

Link together the Freebox and the NAS. Both are close to each other, in the same cabinet. Freebox is already equipped with a 10G SFP+ port. All I need is a NIC and a cable:

| Part  | Model                                           |  Quantity | Total (excl. shipping) | Notes                                                     |
| ----- | ----------------------------------------------- | --------: | ---------------------: | --------------------------------------------------------- |
| NIC   | 10Gtek X520-10G-1S-X8, PCIe x8 single SFP+ port |         1 |                €135.99 | 82599 Intel controller supported by FreeBSD.              |
| Cable | 10Gtek SFP+ Direct Attach Copper - 2m           |         1 |                 €26.99 | A DAC is low-power, low-cost, low-latency and less bulky. |
|       |                                                 | **Total** |            **€162.98** |                                                           |

## Cabinet switch

Home is wired with *Grade 3 Residential Triple Play 4PR F/FTP* cables. Not sure what that cable is. In theory 10GBASE-T requires Cat6. The reality is that most equipment are OK with short-distance Cat5e (less than 30-45 meters). I guess it is worth a try.

RJ45 sockets are available in each room, everything converging in the router & NAS cabinet. Unfortunately the Freebox SFP+ port is capped at level-2 (\<1.5 W), and is not providing enough power for an RJ45 transceiver. So we need an SFP+ switch.

There is plenty of SFP+ modules to choose from. I selected the MikroTik S+RJ10 to reduce incompatibility and for its good price. Other alternatives are covered in this excellent [SFP+ to 10Gbase-T adapter buyers guide](https://www.servethehome.com/sfp-to-10gbase-t-adapter-module-buyers-guide/).

At the end the cabinet was equipped with:

| Part        | Model                                 |  Quantity | Total (excl. shipping) | Notes                                                                                                                                     |
| ----------- | ------------------------------------- | --------: | ---------------------: | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Switch      | MikroTik CRS305-1G-4S+in              |         1 |                €144.01 | [Limited to 2 RJ45 transceivers, after which it gets too hot](https://wiki.mikrotik.com/wiki/S%2BRJ10_general_guidance#General_Guidance). |
| Transceiver | MikroTik S+RJ10                       |         1 |                 €66.04 |                                                                                                                                           |
| Cable       | 10Gtek SFP+ Direct Attach Copper - 1m |         1 |                 €24.99 |                                                                                                                                           |
|             |                                       | **Total** |            **€235.04** |                                                                                                                                           |

## Office switch

This one brings 10G from the cabinet to the home office. That where most bandwidth is consumed. We'll bring 10G by the way of classic copper cables, and have some options for another switch to distribute the bandwidth there:

| Part   | Model           | 10G ports      | 1G ports |    Price | Notes                                                                                             |
| ------ | --------------- | -------------- | -------- | -------: | ------------------------------------------------------------------------------------------------- |
| Switch | QNAP QSW-308S   | 3 SFP          | 8 RJ45   | \$159.00 | Unmanaged                                                                                         |
| Switch | Netgear GS110MX | 1 RJ45         | 8 RJ45   |  €160.65 | Unmanaged                                                                                         |
| Switch | QNAP QSW-308-1C | 3 SFP          | 8 RJ45   | \$200.99 | Unmanaged                                                                                         |
| Switch | Asus XG-U2008   | 2 RJ45         | 8 RJ45   |  €199.65 | Unmanaged                                                                                         |
| Switch | Netgear MS510TX | 1 SFP / 1 RJ45 | 4 RJ45   |  €277.98 | Managed. [Review](https://www.servethehome.com/netgear-ms510tx-review-this-is-one-funky-switch/). |
| Switch | Netgear XS505M  | 1 SFP / 4 RJ45 | 0        |  €314.99 | Unmanaged                                                                                         |
| Switch | Netgear XS508M  | 1 SFP / 8 RJ45 | 0        |  €383.98 | Unmanaged                                                                                         |

## External NICs

To plug the laptops in the office on the 10G network, we'll rely on external dongles. There a wide variety and price point to choose from:

| Part | Model               | Port      | Interface       |    Price | Notes |
| ---- | ------------------- | --------- | --------------- | -------: | ----- |
| NIC  | Club 3D CAC-1420    | 2.5G RJ45 | USB-A 3.2 Gen 1 |  \$41.57 |       |
| NIC  | Club 3D CAC-1520    | 2.5G RJ45 | USB-C           |  \$45.07 |       |
| NIC  | TRENDnet USB-C 2.5G | 2.5G RJ45 | USB-C 3.1       |  \$86.90 |       |
| NIC  | StarTech USB 3 5G   | 5G RJ45   | USB-A 3.0       | \$101.68 |       |
| NIC  | TRENDnet USB-C 5G   | 5G RJ45   | USB-C 3.1       | \$158.20 |       |
| NIC  | QNAP QNA-UC5G1T     | 5G RJ45   | USB-C 3.0       | \$224.00 |       |
| NIC  | Sonnet SOLO10G-TB3  | 10G RJ45  | Thunderbolt 3   | \$149.00 |       |
| NIC  | QNAP QNA-T310G1T    | 10G RJ45  | Thunderbolt 3   | \$178.99 |       |
| NIC  | QNAP QNA-T310G1S    | 10G SFP+  | Thunderbolt 3   | \$169.00 |       |
| NIC  | Sonnet SOLO10G-TB2  | 10G RJ45  | Thunderbolt 2   | \$198.98 |       |

## Wireless

Check out this [Wi-Fi 4,5,6,6E (802.11 n/ac/ax) guide](https://www.duckware.com/tech/wifi-in-the-us.html), which is one of the best resource I ever found to make educated wireless router/AP upgrade decisions, and cut through all the marketing hype.

One of the best access point so far to increase coverage seems to be the Ubiquiti UniFi nanoHD (€163.88).

## Upgrade path

- Upgrade NAS's motherboard and get one with an onboard 10G controller, to eliminate the PCI-e card.
- Get rid of all external USB NICs and replace them with all-in-one USB-C hubs with embedded 10G. No solution exists on the market yet.
- Buy a new house, install optical fiber everywhere.
