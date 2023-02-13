# piscanner

This is the service which coordinates the primary functionality of the
[magic scanner](https://github.com/nhsx/il-magic-scanner).

It is a Python service, written to be run under the system Python on
Raspberry Pi OS Bullseye (currently 3.9.2).

## Installation

### Package dependencies

`piscanner` is designed to work with the system python, so relies on
system python packages.  They are installed by the
[ansible](../pi-ansible-config) scripts, but for reference the
packages you will need are:


```
$ sudo apt install \
	ffmpeg \
	python3-picamera2 \
	python3-gpiozero \
	python3-tesserocr \
	imagemagick \
	python3-aiohttp \
	python3-websockets \
	python3-opencv \
	python3-smbus \
	i2c-tools
```

### Service dependencies

Before attempting to run `piscanner`, make sure you have installed the
`[ledd](../ledd)` and `[keebd](https://github.com/nhsx/il-keebd)`
services and have them running at boot.

### piscanner itself

Run:

```
$ sudo make install
```

This will copy the Python source to `/opt/piscanner/`, and install a
`piscanner.service` systemd unit.  You can use `systemctl` to start
and stop the service in the usual way (that is, `sudo systemctl start
piscanner` will start the service).  It will start at boot.

Once you have installed the service, you will need to separately
download a `.weights` file from
[here](https://github.com/nhsx/il-magic-scanner/releases/tag/v1) and
put it in the right place.

To download and install the weights file, run:

```
$ cd /tmp/
$ wget https://github.com/nhsx/il-magic-scanner/releases/download/v1/scanner-yolov4-tiny_final.weights.bz2
$ bunzip2 scanner-yolov4-tiny_final.weights.bz2
$ sudo mv scanner-yolov4-tiny_final.weights /opt/piscanner/model/backup/
```

## Hardware config

### The camera

You will need a camera module plugged into the pi.  I used a v2.1.
With a v2.1 camera module you can manually set the focal length.  See,
for instance,
[here](https://projects.raspberrypi.org/en/projects/infrared-bird-box/6)
for instructions on how to do this.

The camera module v3 has autofocus, and I haven't tested this to know
whether it works in our application.

### The Button

The `piscanner` script expects to be triggered by a button press.  The
button should be momentary push-to-make, and connected between [GPIO
pin
17](https://projects.raspberrypi.org/en/projects/physical-computing/1) and GND.

### The LEDs

See [here](../ledd) for hardware information on connecting the LEDs.

### Power

The raspberry pi will need its own power supply.  Use an official
Raspberry Pi power supply plugged into the `PWR` port.

### USB cable

Plug a USB micro cable between the other USB micro port on the pi and
a USB port on the computer you intend to receive scanned data.

## Usage

With the `piscanner` service running, to scan a phone:

- On the receiving computer, put the keyboard focus in a text input
  element.
- Log in to the NHS app, and if necessary navigate to the home screen,
  scrolled to the top.
- Orient the phone so the upper portion of the screen, with your name
  and NHS number, is visible to the camera and upright.
- Press the scanner's button.  You should see indication from the LEDs
  that it's processing the image.
- If the scanner was able to extract name and number, you will see
  these typed into the text input element on the receiving computer.

## Author

Alex Young <alex.young12@nhs.net>
