# Piscanner Ansible Config

This is an Ansible config to bring a fresh Raspberry Pi OS image up to
a state where development can happen on it, it can run the
[piscanner](../piscanner) and associated services, and it can run its
own WiFi access point so that you can get an SSH shell without needing
to configure the scanner to join an existing WiFi network.

You will need:

1. A Raspberry Pi.  I used a Zero 2.  You *may* have luck with a 3A+,
   a 3B+, a 4, or a 400.  I haven't tried any of them.
2. An SD card.  I use Samsung Edge A1 cards, because they're nice and
   fast without being horrid and expensive.

## Usage

### Install ansible

First, install `ansible`.  That's platform-specific and beyond the
scope of this README.

### Configure and Install Raspberry Pi OS

Using the [Raspberry Pi
Imager](https://www.raspberrypi.com/software/), click `Choose OS` and
select `Raspberry Pi OS Lite (32-bit)` from the `Raspberry Pi OS
(other)` menu.  Click the cog button that appears, to bring up the
advanced options menu.  You will want to allow Imager to pre-fill
your wifi config.

Set the hostname to `piscanner`.  The `ansible` config assumes this is
the hostname you've set.  If for some reason you can't use that
hostname (say, you've already got something on the network with that
hostname, or you're doing more than one of these), then pick a name
here and make sure to edit the file called `hosts` so that it matches
whatever you pick.

Enable SSH. It's best to use public-key authentication only, but you
do want to set a password for the `pi` user.

Under the `Configure wireless LAN` section, make sure that the
`Wireless LAN country` setting is correct.

Click `Save`, and plug in an SD card if you haven't already.  `Choose
Storage` to select that card, then `Write`.  At this point you have
enough time to go and make a cup of tea.

### Drink tea

Drink your tea.  It is important that you do not rush this step.

### Boot the Pi

Once you have finished your tea, because you took the correct amount
of time to do so, the write will have finished.  Extract the SD card
from the machine you've used to image it, plug it into your Raspberry
Pi, and switch it on.

When you boot it for the first time, it will take a significant length
of time to appear on the network because it needs to resize the
filesystem for the SD card on the first boot.  On OS X and a compliant
network, I find it useful to run this in a console while that's
happening so I know when it's ready:

```
$ while ! ping piscanner.local; do echo "not yet"; done
```

What that's doing is repeatedly trying to look up the `piscanner` host
on the local network.  When the Raspberry Pi has got far enough
through its boot sequence that it can successfully connect to the wifi
network you configured in the Imager, it'll start responding to pings.

### Run ansible

If the pi is responding to pings, that means you can SSH to it, and
that means `ansible` can run.  I've provided a `Makefile` to simplify
this a little. Run:

```
$ make first
```

This will prompt you for a sudo password, which you will only need to
provide the first time you run `ansible`.  Subsequent runs, if you
change the config, can be run simply as:

```
$ make
```

Since the first execution of `ansible` has some work to do, you may
find that this is an appropriate juncture for more tea.

## Wifi Access Point

As mentioned above, the scripts in `roles/hostap` will configure the
pi such that it can offer its own wifi access point.  Once `ansible`
has been run the first time, the scripts to switch between wifi access
point mode and client (or "station") mode are at
`/usr/local/sbin/become-hotspot` and `/usr/local/sbin/stop-hotspot`.
You will need to reboot the pi after running either to switch mode
back and forth.

### Enabling the hotspot

To enable the inbuilt hotspot, connect to the pi and run:

```
$ sudo /usr/local/bin/become-hotspot
$ sudo reboot
```

You will be unceremoniously disconnected.

A short time later - 25 seconds or so - if you open your network
control panel you will be able to see a new SSID available to connect
to, called `piscanner-123`.  Connect to it with the passphrase
`comeonbarbieletsgoparty`.  Once connected, you will be able to
reconnect to the piscanner by running:

```
$ make sh
```

You will want to enable the inbuilt hotspot any time you are going to
take the pi anywhere it won't be able to join an existing network.

### Disabling the hotspot

To switch from the inbuilt hotspot to a predefined network, connect to
the pi and run:

```
$ sudo /usr/local/bin/stop-hotspot
$ sudo reboot
```

As before, your SSH connection will be killed, and a short time
later - 25 seconds or so - you will be able to run `make sh` to get a
new one.

## Backups

If you're doing significant work on the pi (which you can), you'll
want to be able to sync that work off the pi.  To that end there's a
`make backup` task you can run to sync `~/src` off the pi into a local
`backup/` directory.

## Author

Alex Young <alex.young12@nhs.net>
