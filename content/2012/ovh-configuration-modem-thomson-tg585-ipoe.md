---
date: '2012-07-03'
title: 'OVH: configuration du modem Thomson TG-585 en IPoE'
category: Français
tags: ADSL, dslam, ipoe, Modem, nra, ovh, PPPoE, telnet, thomson
---

![Thomson TG585 v8 web interface logged in as Administrator, reporting software release 8.2.P.G and the broadband connection as IPoE connected](thomson-tg585-ipoe-admin-panel.png)

OVH migre l'un après l'autre ses [points de collecte ADSL](https://www.ovh.fr/adsl/degroupage-nra-ovh.xml) vers leur infrastructure interne. Lors de la bascule, il faut reconfigurer son modem pour qu'il se connecte directement en `IPoE` et non plus en `PPPoE`.

J'ai souscrit à l'[offre no!Box](https://www.ovh.fr/adsl/no_box.xml) avec un modem [Thomson TG-585 v8](https://web.archive.org/web/20120622115612/http://www.technicolorbroadbandpartner.com/dsl-modems-gateways/products/product-detail.php?id=214&seg=3). Ce modem ne supporte pas par défaut le protocole `IPoE`. Vous devez le reconfigurer, mais la procédure indiquée par OVH dans leur mails n'est pas très claire.

![Telnet session into the router, its ASCII-art honeycomb banner filling the terminal above the administrator prompt](thomson-tg585-router-login.png)

En fait, il faut appliquer la même procédure que celle indiquée pour le modem dit "PRO". On trouve ces [instructions sur le wiki d'OVH](https://web.archive.org/web/20120825192437/http://guide.ovh.com/ADSLConfigIpoe), et je vous confirme qu'elles fonctionnent parfaitement pour le modem Thomson TG-585.

Et donc, après s’être connecté depuis un terminal sous Linux en telnet:

```shell-session
$ telnel 192.168.1.254
```

Il ne reste qu'à exécuter les commandes suivantes depuis le prompt du modem:

```console
system reset factory yes proceed yes
wireless mssid ifconfig ssid_id 0 secmode wpa-psk WPAPSKversion WPA2

ppp ifdelete intf Internet
ppp relay flush

ip ifadd intf IPoE dest ethoa_8_35
ip ifattach intf IPoE

dhcp client ifadd intf IPoE
dhcp client rqoptions add intf IPoE option default-routers
dhcp client rqoptions add intf IPoE option domain-name-servers
dhcp client ifattach intf IPoE

ip ifadd intf Wan dest eth-wan
ip ifattach intf Wan
dhcp client ifadd intf Wan
dhcp client rqoptions add intf Wan option default-routers
dhcp client rqoptions add intf Wan option domain-name-servers
dhcp client ifattach intf Wan

nat ifconfig intf Wan translation enabled
nat ifconfig intf IPoE translation enabled

dhcp server config state enabled

service system ifadd name PING_RESPONDER group wan

dsd config state disabled

ip ipdelete addr 10.0.0.138

system config defaultconnection IPoE led green

env set var CONF_SERVICE value IPoE

cwmp config state=enabled mode=full periodicInform=enabled periodicInfInt=86400 maxEnvelopes=1

cwmp server config url=https://94.23.114.8:7777/

saveall

system reboot
```
