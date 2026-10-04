---
date: '2005-04-19'
title: Créer un Espace de Stockage Fiable avec RAID 5 et LVM sous Linux
category: Français
tags: Backup, boitier externe, CLI, disque dur, firewire, Hardware, informatique, Linux, LVM, Mandriva, mdadm, openbrick, ordinateur, RAID, USB, XFS
---

Cet article explique comment créer un espace de stockage redondant et fiable en utilisant du matériel grand public et bon marché. Cela est possible par la combinaison de Linux, des mécanismes RAID logiciel et du gestionnaire de volumes logiques LVM.

_**Mise à jour**: Le but initial était d'utiliser des boîtiers externes USB pour construire une matrice RAID. En réalité je n'ai jamais pu obtenir de résultats convaincants car les disques USB ne sont pas aussi fiables que des disques dur IDE classique. Je m'explique: une partie seulement des instructions IDE trouvent leurs équivalents dans le protocole USB, limitant ainsi l'accès bas niveau aux disques durs externes par le kernel linux. Voila pourquoi cet article reste inachevé et que certaines parties ci-dessous peuvent paraître décousues._

Pour commencer une [explication de la technologie RAID](https://fr.wikipedia.org/wiki/RAID_%28informatique%29) et de ses intérêts n'est pas superflu.

Je dispose de 2 disques durs de 120 Go, que je met chacun dans un boîtier externe USB 2. Je les branche ensuite sur mon [OpenBrick NG](https://web.archive.org/web/20060822232700/https://www.storever.com/product/openbrick/openbrick-ng) qui possède sur son port IDE0 un disque dur de 160 Go qui héberge l'OS. L'OS en question est une Mandrakelinux 10.0 installée sur les 40 premiers gigas du disque IDE, dans des partitions classiques qui ne seront pas protégées par le RAID. J'ai choisi une Mandrakelinux 10.0 car à l'époque la Mandriva 2005 n'était pas encore disponible et la Mandrake 10.1 à un `udev` buggé qui ne créée pas les devices RAID (donc impossibilité d'activer automatiquement le RAID au démarrage).

Supposons à partir de maintenant que l'OS est installé, pour nous concentrer uniquement sur la configuration et la mise en route du RAID.

## Étape 1: Formater les partitions

J'ai donc les devices suivants:

- `/dev/hda` -> DD de 160 Go (40 Go pour l'OS et 120 Go de libre)
- `/dev/sda` -> DD externe de 120 Go n°1
- `/dev/sdb` -> DD externe de 120 Go n°2

Nous voulons créer une matrice RAID 5 à partir de 3 x 120 Go. Plutôt que de faire une seule grosse partition de 120 Go par disque, nous allons créer dans chacun des disques trois partitions de 40 Go (3 x 3 x 40 Go = 3 x 120 Go). Nous construirons ensuite 3 unités RAID 5 de 3 x 40 Go puis nous les assemblerons via LVM. L'intérêt de diviser nos grosses partitions en plus petites est de réduire considérablement (par un facteur 3 dans notre cas) le temps de régénération de nos unités RAID en cas de corruption d'une partition.

Les partitions à créer sont de type Linux RAID. On pourra éventuellement faire cela avec `drakconf`.

## Étape 2: Configuration de la matrice RAID

Nous utiliserons `mdadm` pour la gestion de notre RAID.

_Note_: A partir de la 10.1, la version de `webmin` fournie avec la Mandrake supporte `mdadm`. Pour arriver à nos fins par ce moyen, on pourras s'inspirer d'un [article sur la mise en place d'un RAID via webmin](https://web.archive.org/web/20050106202748/http://froverio.online.fr/articles.php?lng=fr&pg=55).

Installation de mdadm:

```shell-session
$ urpmi mdadm
```

Création des matrices:

```shell-session
$ mdadm --create --verbose /dev/md0 --level=5 --raid-devices=3 /dev/hda2 /dev/sda2 /dev/sdb2
$ mdadm --create --verbose /dev/md1 --level=5 --raid-devices=3 /dev/hda3 /dev/sda1 /dev/sdb1
$ mdadm --create --verbose /dev/md2 --level=5 --raid-devices=3 /dev/hda4 /dev/sda3 /dev/sdb3
```

Lors de la création, les paramètres par défaut sont suffisants. Pour information, les paramètres optimaux sont:

- Parity: left symetric
- Persistent super block
- Chunk size: 32kb ou 64kb (pour nos partitions de 40 Go)

Éditons le fichier de configuration `/etc/mdadm.conf`:

```text
DEVICE          /dev/sda*
DEVICE          /dev/sdb*
DEVICE          /dev/hda2
DEVICE          /dev/hda3
DEVICE          /dev/hda4
ARRAY           /dev/md0 devices=/dev/hda2,/dev/sda2,/dev/sdb2
ARRAY           /dev/md1 devices=/dev/hda3,/dev/sda1,/dev/sdb1
ARRAY           /dev/md2 devices=/dev/hda4,/dev/sda3,/dev/sdb3
```

Avant d'aller plus loin, il faut attendre que les matrices soient construites:

```shell-session
$ watch -n1 'cat /proc/mdstat'
```

Dans mon cas, cela à nécessité entre deux et trois heures pour chaque unité RAID.

_Note_: avec la Mandrake 10.1, lors de la création des matrices RAID, on aurait eu des problèmes du type `raidstart failed : /dev/md1: No such file or directory`, qui peuvent être résolus en créant les device manuellement:

```shell-session
$ mknod /dev/md0 b 9 0
$ mknod /dev/md1 b 9 1
$ mknod /dev/md2 b 9 2
```

Ces commandes créent les unités RAID dont nous avons besoin. Malheureusement elles ne sont pas autodetectées au démarrage donc, dans le cas d'une mdk 10.1, il aurait fallu faire cette manip à chaque démarrage de la machine. Voila une bonne raison pour ne pas utiliser la version 10.1.

## Étape 3: Agréger les matrices RAID via LVM

J'ai choisi LVM pour agréger les unités RAID, pour bénéficier d'un redimensionnement flexible de mon espace disque, avant de parer à tous les scénarios possibles auxquels je serais confronté dans le futur. Il est tout à fait possible de faire la même chose avec du RAID linéaire (voir l'étape "3-bis" ci-après), mais dans ce cas on perd la une certaine souplesse au niveau des partitions.

Installation de LVM:

```shell-session
$ urpmi lvm2
```

On peut consulter la liste des disques parents sur le système avec `lvmdiskscan`.

Ensuite il faut créer un volume physique (PV = Physical Volume) pour chaque unité RAID:

```shell-session
$ pvcreate /dev/md0
$ pvcreate /dev/md1
$ pvcreate /dev/md2
```

Créons maintenant un groupe de volumes contenant nos trois partitions :

```shell-session
$ vgcreate vg01 /dev/md0 /dev/md1 /dev/md2
```

(marche pas ???)

## Étape 3-bis: Agréger les matrices avec du RAID linéaire au lieu d'utiliser LVM

Si vous voulez utiliser du RAID linéaire plutôt que LVM, il faut créer une nouvelle unité RAID sur la base des trois premières:

```shell-session
$ mdadm --create --verbose /dev/md3 --level=linear --raid-devices=3 /dev/md0 /dev/md1 /dev/md2
```

Puis penser à mettre à jour `/etc/mdadm.conf`:

```text
DEVICE          /dev/sda*
DEVICE          /dev/sdb*
DEVICE          /dev/hda2
DEVICE          /dev/hda3
DEVICE          /dev/hda4
DEVICE          /dev/md0
DEVICE          /dev/md1
DEVICE          /dev/md2
ARRAY           /dev/md0 devices=/dev/hda2,/dev/sda2,/dev/sdb2
ARRAY           /dev/md1 devices=/dev/hda3,/dev/sda1,/dev/sdb1
ARRAY           /dev/md2 devices=/dev/hda4,/dev/sda3,/dev/sdb3
ARRAY           /dev/md3 devices=/dev/md0,/dev/md1,/dev/md2
```

## Étape 4: Créer le système de fichier

Formater en xfs:

```shell-session
$ mkfs.xfs -f /dev/md3
```

J'ai choisi xfs comme filesystem car il peut être agrandit à chaud, lorsque la partition est montée.

Pour monter le tout:

```shell-session
$ mkdir -p /mnt/data
$ mount /dev/md3 /mnt/data
```

Et enfin, pour le montage automatique au démarrage de notre serveur, il faut ajouter la ligne suivante à notre fichier `/etc/fstab`:

```text
/dev/md3 /mnt/data xfs defaults 0 0
```

## Maintenance du système

- Réintégrer une partition dans la matrice.

  Si une partition est éjectée d'une unité raid (par exemple `sda1` sur `md1`), il faut faire:

  ```shell-session
  $ cat /proc/mdstat
  $ mdadm --examine /dev/sda1
  $ mdadm /dev/md1 -a /dev/sda1
  $ cat /proc/mdstat
  ```

  La première commande montre que le RAID est dégradé. La seconde commande examine le status du disque qui à été éjecté de la matrice. La troisième ligne permet de réintégrer à chaud la partition dans la matrice. Et enfin la dernière commande nous montre l'avancement de la reconstruction de la matrice (ce qui peut prendre pas mal de temps).

- Ré-assembler une matrice.

  La commande est du type:

  ```shell-session
  $ mdadm --stop /dev/md0
  $ mdadm --assemble /dev/md0
  ```

  Attention `--assemble` se base sur le fichier `/etc/mdadm.conf`.

- Créer une unité RAID dégradée.

  La commande suivante créée une unité RAID 5 sur 3 disques durs, en indiquant que le premier est absent via le mot clé `missing`:

  ```shell-session
  $ mdadm --create /dev/md0 --level=5 --raid-devices=3 missing /dev/hda1 /dev/sda1
  ```

## De la lecture complémentaire sur RAID 5 et LVM

- [Notes on Building a Linux Storage Server, by Martin Smith](https://web.archive.org/web/20050307031125/http://www.ethics-gradient.net/myth/storage.html)
- [Gentoo Install on Software RAID mirror and LVM2 on top of RAID](https://web.archive.org/web/20050415000057/http://gentoo-wiki.com/HOWTO_Gentoo_Install_on_Software_RAID_mirror_and_LVM2_on_top_of_RAID)
- [Disks are fun](https://scottstuff.net/blog/articles/2005/01/10/disks-are-fun)
- [Anatomy of a Drive Failure](https://scottstuff.net/blog/articles/2005/01/08/anatomy-of-a-drive-failure)
- [Changing RAID Drives Without Losing Data](https://web.archive.org/web/20050308123107/http://www.digitalmapping.sk.ca/Networks/ExpandingRAID.htm)
