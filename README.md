# The Magic Scanner

## Setting The Scene

When you walk into A&E, the very first interaction you will have is
with the triage desk.  The hospital needs to know who you are.  Apart
from any administrative checkpointing, what the hospital want at that
point is a route in to your medical records.

The conversation that tells A&E who you are sounds simple, but it can
hide frustrating complexity.  Just the first question they'll ask -
what is your name? - can go down a rabbit-hole of misheard accents,
uncommon spellings, and unexpected cognitive difficulties.

Obviously a name alone isn't enough to identify someone.  They'll ask
for your date of birth, too, but even then, clinical mistakes have
been made where the same name and birthdate are shared by two
individuals.

To ensure they have identified *you*, and not someone else who happens
to have your name and birthday, what they really want is your NHS
Number.  But it is a rare patient who will know that off the top of
their head, or who will bring a GP letter with them to A&E.

Our hypothesis was this: if we can scan the information that the
triage desk wants out of the patient's phone, rather than have them
narrate it, we can solve three problems: first, the slow, face-to-face
"no, spelled with an 'E', two 'L's" conversation is short-cut; second,
we can bring additional information to the interaction in the form of
the NHS Number; and third we can get it right first time.

### The Patient ID QR Code

Our intent is that the NHS App should present a QR code containing the
relevant information, on the home screen.  QR codes are easy to
generate and easy to scan.  The way an off-the-shelf £25 barcode
reader from Amazon works is that it pretends to be a USB keyboard:
when you scan a QR code, what the computer it's plugged into sees is
as though someone was sat there typing in the data encoded in the QR
code.  That makes them extremely easy to physically integrate.  And
when you sign in to the NHS App with an NHS Login that is sufficiently
assured, it has all the information we want to present, so all the
technical parts are straightforward.  However, there is a roadblock in
our way.

If we want to make a change in the NHS App, that effectively means
rolling it out nationally.  Before any hospitals are signed up.  We
don't have the cohorting ability to only roll out the QR code to
people who are going to turn up at a specific A&E: in general people
don't schedule falling off their ladders for us, convenient though
that would be.  That means we'd be introducing a potentially confusing
feature into the system before anyone could either explain what it was
or, equally importantly, prevent complaints at hospital front desks
that they couldn't read this fancy new QR code thing that had just
appeared in their app.

So: we need to prove that the idea has legs so we know that the idea
is worth making the investment in to push it out as a major new
feature across the system.  And this is where it gets a bit fiddly.

The experiment we want to do is to have people turn up at the A&E
desk, sign in on their phone with no other prep, scan in, and give the
hospital a high degree of confidence that they've got the right data.
With that, we can measure the time-at-desk both with and without the
scanning, and demonstrate how much time we can save the system.

However, without being able to get a QR code into the NHS App itself
as a trial, the next most obvious option is that we stand up a
parallel service to generate the QR code.  This service would be
fronted by NHS Login, so people could use exactly the same credentials
as they use for the NHS App, and it as only purpose would be to put a
scannable code on the phone's screen.  This would be technically
simple to build and operate.

You can guess that this route is not all plain sailing, though.  It
turns out that roughly half of all NHS App users log in with the
biometrics - fingerprint, faceID, whatever - on their phone.  That
biometric login wouldn't be available to our QR code service, so
anyone logging in for their QR code would need to go through a
password-based NHS Login flow.  Now, I don't know about you, but if
I've not logged into a service with its password since setting it up
years ago, I'm very unlikely to remember the password; this is doubly
true if I'm stressed because something's happened that's landed me in
A&E.  So anyone signing into our service will probably have to go
through a password recovery process, and you can very quickly see how
with the right confluence of queue length and time at desk, we end up
in a situation where the triage staff are waiting for the person in
front of them to finish signing in.  We'd have created a delay where
previously there wasn't one.

So this approach is largely ruled out.  We can't risk making things
worse otherwise no hospital is going to be interested in helping us to
run the trial.

### Or Not

And that's how we end up with this repository.  The fundamental
question we want to answer has nothing to do with QR codes, and
everything to do with the ergonomics of scanning the phone.  As long
as we can test "patient approaches desk, scans phone, is signed in"
and the timings around it, it doesn't matter what's shown on the
phone's screen.

So, we thought, why don't we just read the data off the home screen of
the app?  It has the name and the NHS Number, it's a known layout.
Can we design a scanner which will pluck that off the screen and
present it as though it *was* scanned by a barcode reader?

This repository is the code, CAD, data, and documentation of that
scanner.

## The Magic Scanner Operating Principle

We know that the scanner needs to:

1. Take a photo of the screen
2. Identify where the data we want is
3. Do some character recognition to turn right parts of the photo into text
4. Send that text to a USB host, as fake keypresses

And it has to do all that in a short enough time period that the
reception staff don't get annoyed with it or think it's broken; and it
has to be cheap enough that we'd be able to build a few of them
without breaking the bank.

Of all the steps, step 2 intrigued me the most.  That sort of object
recognition and bounding box extraction is a classic machine learning
task, and how well we could perform that job would put a limit on the
quality of data that the scanner would present to the user.

My first thought was to give a Raspberry Pi a try.  They have several
things going for them, most importantly for this project a) good
camera and USB gadget support; b) excellent software availability and
community activity; and c) I had a Pi Zero 2 sat next to me.

The importance of point c) shouldn't be underestimated.  We needed to
demonstrate that we could build a working prototype to test the
software and the ergonomics in days, not weeks, and having hardware
available off-the-metaphorical-shelf enabled us to go from idea to
first physical prototype between the Thursday of one week and Tuesday
the next.  Further refinement and a mk2 followed.

There were questions in my mind while making that choice, though: for
instance, would the processor in the Zero 2 have enough power to run
the machine learning model?

## The Build

### Physical Shell: the Mk1

Unfortunately the licensing situation in this project doesn't let me
share the original FreeCAD model itself, but I've put the `.step` file
[here](cad/piscanner-mk1.step) and the `.stl` (which github will
render for you as a pretty picture) [here](cad/piscanner-mk1.stl).
The reason is that the CAD model has a dependency on some third party
`.step` files that I don't have a licence to distribute.  When I get a
chance to come back and clean up the dependencies I will be able to
share the FreeCAD document, but until then, this is the best I can do.

There are a couple of things to note about the design of the mk1, both
good and bad.


#### 1. The Trigger Mechanism

I needed a button press to trigger taking the photo and processing it.
In my first version I thought it best to hide the button and see if I
could make the physical interaction as simple as possible.  In this
version there is a pair of buttons mounted under the window that the
Pi's camera peers through, such that when you press the phone
face-down onto the window, the window frame flexes and allows contact
to be made.  It's a mechanism which puts the phone screen at a
well-controlled distance from the camera lens.  This is important,
because the Pi Camera Module v2.1 is fixed focus.  They come from the
factory with a focal point out at infinity, and need to be refocused
to take good pictures of close objects.  The scanner needs not to be
too tall so I refocused the lens almost as close as I could, but until
I'd built the thing I didn't have a good way to check how much depth
of field I had to work with.  So this mechanism let me ensure that the
screen was in a precise place when the buttons were pressed.

If I were to build this mechanism again, there is a change I'd make in
that the current design puts the buttons on top of a pair of towers
attached to the base.  That attachment point is fine - I intentionally
wanted to be able to pull all the electronic guts out without too much
stress because I knew I was likely to want to change it around - but
the change I would make is to make the towers removable.  The distance
you need to depress the buttons I used to get a contact is sub-mm, and
the dimensional stability of the 3d printing process I used to make
the shell isn't great for this sort of design.  I wanted to be able to
swap out the towers to tweak their heights so the offset from the
flexible frame was better, but couldn't.

#### 2. The Absence Of Any Feedback Whatsoever

In the time available I just didn't have the opportunity to put any
status lights or readouts on the outside of the device.  I knew how I
was going to, it just fell outside the scope of a quick prototype
whose purpose was to prove the data pathway.


#### 3. The Raspberry Pi mounting

Rather than figure out the dimensions of a raspberry pi zero, I
figured that I could just reuse an existing case and clamp that into
place, giving me a single thing to position correctly on the base of
the scanner than having to worry about separately mounting the pi and
its attached camera.

This was a mixed blessing: the
[case](https://www.raspberrypi.com/products/raspberry-pi-zero-case/)
obviously fits the parts perfectly, but is a rather interesting shape,
which made cutting an accurate slot for it in the model something of a
challenge.  If I'd had a rather more rectilinear case to hand I would
have used that instead and simplified the job.

#### 4. Other flaws

In my rush, I underestimated how much clearance a USB plug needs.
There's not nearly enough clearance inside this body for a
conventional USB-micro plug to fit, and I ended up cutting a hole in
the wall for the USB keyboard cable.

There are a few other design details I could have done better and
suspected were a problem at the time, but sort of got away with.  The
mating interface between the base and the upper shell made the upper
hard to 3d print, for instance, and the attachment point for the
flexible window frame didn't have enough vertical bracing so the angle
of the window was dependent on the tightness of the bolts holding it
on.  Not ideal.

Purely by chance, at no point in the lifespan of the mk1 did I need
access to the SD card.  Lacking any way of getting at it which
wouldn't involve a complete disassembly was a conscious choice, but
one I would rectify later.

### Machine Learning

The scanner needs to be able to pull out small, specific chunks of the
pictures it takes, so that it can feed them to optical character
recognition software.  As I said above, this is an absolutely classic
machine learning task, but just knowing that it's possible is a world
away from having a working implementation that does the thing when you
press the button.

I simplified the problem of going from idea to implementation by
restricting the type of model I would look at to the YOLO family.
These are very fast, accurate enough object recognising neural network
systems that are popular enough in the industry that the tooling and
support around them is very good.  This meant that I had a choice of
implementation tooling.

Based on the availability of samples and documentation, I picked
`darknet` as a training platform and, initially, as the inference
platform that the scanner would execute when the button was pressed.

There is a terraform script for provisioning an AWS GPU instance (I've
picked `g3s.xlarge` as the cheapest spot instance size available) in
[here](gpu-terraform). It takes care of grabbing the
`darknet` source and building it.  Note that it *also* provisions a
smallish jump host as a non-GPU instance so that you can have a stable
jumping-off point that's not so expensive to run.


#### Model Selection

To cut a short story even shorter, given the time constraints I didn't
want to mess about trying to find a network architecture that would
work, I needed to pick something off the shelf that I could reuse
without too much hassle and would have enough power, and the right
inputs and outputs, for the task.  The YOLO family of network
architectures fit the bill, and specifically the YOLOv7 looked like it
would have the performance characteristics we need.  It's also popular
enough that there is a lot of guidance available online for using
it. There's a premade `darknet` config for it, so it looked like it
would be reasonable to start there and only change that decision if it
turned out either to be too slow, or not accurate enough.


#### Training Data

We want the network to be able to put a bounding box around two items
of text on the phone screen: the patient's name, and their NHS number.
Given the constraints of the physical device, there's actually not
much variation we should expect in the pictures we'll be putting
through the network.  The home screen of the NHS App is very
constrained, visually speaking: it's a consistent font, there are very
consistent markers around the image, colours should only be in a
certain range, and so on.  That makes the job of putting together a
training data set simpler than it might otherwise be.

We're also helped here by a very useful technical detail: the NHS App
is (to simplify slightly) just a web site.  You can visit the site
online in a browser, and you can view the source.  If you resize the
browser window to be mobile phone shaped, it renders the same as if it
was on a phone.

So, I did that, grabbed the resulting web page, and saved it.  I then
edited the HTML to replace my name and NHS number with [python
template
markers](https://docs.python.org/3/library/string.html#template-strings).
That enabled [this script](TODO) to generate an arbitrarily large
number of fake NHS App home screens, each with their own name and
number. [^1]

Next, I used [this script](TODO) to take screenshots of each fake with
[selenium](https://selenium-python.readthedocs.io/).  It's not just
the screenshot you need, though: to train the network to put the
bounding box in the right place, you also need to capture where the
bounding box is.  Fortunately that's made available by the browser
API, so we can directly read the bounding box out and save it to a
JSON file.

If you've been following along, you'll now have a directory full of
screenshots of the NHS App homepage, along with the bounding boxes of
where the information we want is.  That's all well and good, but we
need our scanner to be robust to the sorts of noise and distortion
that taking a photo of a phone screen under only semi-controlled
conditions will be subject to.  For this, I leaned on the
[albumentations](https://albumentations.ai/docs/#getting-started-with-albumentations)
tool.  [This script](TODO) is what drives it, and you can see the list
of different types of distortion it applies for me:

```
[
    A.ShiftScaleRotate(shift_limit=0.0625,
                       scale_limit=0.5,
                       rotate_limit=10,
                       border_mode=cv2.BORDER_CONSTANT, value=(128,128,128),
                       p=0.75),
    A.GaussNoise(),
    A.Blur(blur_limit=3),
    A.OneOf([
        A.OpticalDistortion(p=0.3),
        A.GridDistortion(p=0.1),
    ], p=0.2),
    A.OneOf([
        A.CLAHE(),
        A.RandomBrightnessContrast(0.5)
    ], p=0.3),
    A.HueSaturationValue(p=0.3)
]
```

So that's a selection which simulates a few different ways the phone
can be out of position, or registering funny colours, or dirty, and so
on.

I generated many, many training images.  90,000, in fact.  This turned
out to be far too many to be practical and far more than was needed,
but at that point I reasoned that it was better to aim high because I
could always use a subset.

#### Training

Mechanically, the process of training was a matter of uploading the
training data into AWS and getting it onto a GPU instance, then just
running `darknet` with the right parameters.  A word to the wise:
generate the training data where you're going to do the training.
Don't put yourself in the position of needing to upload 5GB of images
over residential broadband.

ANYWAY.

The YOLOv7 architecture learned from this dataset *fast*.  Fast is
relative, but I had a usable network for testing with in half an hour
or so, and in an hour or so `darknet` reported it was done. Nowhere
near the overnight runs that I was expecting.

From this I can intuit that the YOLOv7 architecture is *dramatically*
overpowered for this use case.  The question is whether this matters.
More on this shortly.

### USB Tomfoolery

Taking a brief break from the world of machine learning, there are a
couple of prosaic interface concerns which I needed to deal with.  One
of these is the need to replicate the data flow of a handheld QR code
scanner: to get the data across a USB cable, as though typed into a
keyboard.

Fortunately, making this simple is the Raspberry Pi Zero 2 hardware.
It has two micro-USB ports, one of which supports USB-OTG, which is
what a USB port needs to support if you want to connect it as a USB
*device*, rather than as a USB *host*.  Once set up as a USB gadget,
whether the USB host at the other end of the USB cable is detected as
a hard drive, a modem, or a keyboard is a matter of software
configuration.

In [this directory](TODO) you will find a tool to configure the
raspberry pi such that it pretends to be a keyboard.

Now, that's only half of the story.  When you think of sending data
and pretending to be a keyboard, it's clear that you can't just send
arbitrary data.  You can't send a `NULL`, for instance: there's no key
for that on the keyboard.  So we need a conversion that takes data,
and converts it into the corresponding keypresses.  Fortunately for
our purposes, the conversion is easy in that we only need to be able
to send things that are typeable: a name, a number, and some spaces.

In [this directory](TODO) is a service that runs on the raspberry pi
whose job it is to take data (from something else running on the
machine), strip out anything it can't pass on, and convert the
remainder into keypresses.  It's not very general, in the sense that
there's a lot that in theory is typable which it ignores, but it does
enough for our purposes and is extensible if a need surfaces.  It's
standalone enough that I've spun it off as its own project; I'm sure
it'll come in handy in other circumstances.

## Mk2

### The Hardware

Having shown the mk1 to the team, there were several changes that
needed making.

The flex plate to trigger the button was deemed too much of a leap:
while it's a neat mechanism, people can be hesitant to touch their
phone screens to anything.  And if the screen is cracked, it could
actually cause the image to be corrupted in a way that neither the
phone's owner nor the person on the other side of the desk could see
to know that anything was wrong.  So that went, replaced by a button
on the outside of the case for the reception staff to press.

The lack of a visual feedback mechanism was also a problem, so I
planned to add a row of LEDs.  That's a fairly straightforward change:
more below.

There were a couple of other tweaks to make the case easier to 3d
print.  I redid how the upper shell and the base to which the
electronics are mounted mate together, for a start: the mk1 needed
rather a lot of support material in the print, and that's a waste of
material if it can be avoided.  The aren't any internal columns on
this version, and there's a proper clearance hole for the USB cables.

I also added a vanity plate with our unofficial team logo, because -
well, why not.

As with the Mk1, I can't share the FreeCAD file just yet, but
[this](cad/piscanner-mk2.stl) is what it looks like (`.step`
[here](cad/piscanner-mk2.step)).  It has a footprint a little larger
than the mk1 to accomodate some additional electronics.


### Blinkenlights

Mk1 of the scanner had no feedback mechanism, and that was a problem.
Fortunately adding status LEDs is a fairly straightforward
proposition: there is a very cheap board [you can get](TODO) which is
designed for lighting LEDs in interesting patterns, which you can plug
it into the I2C pins of a raspberry pi's GPIO interface and talk to it
over a simple API.

I couldn't find any direct support for the PCA9685 board aimed at the
raspberry pi, but it is very well supported in the [micropython](TODO)
[ecosystem](TODO).  I [shamelessly](TODO) [nicked](TODO) the support
code and wrote a [very thin shim](TODO) to reuse it so I didn't have
to figure out how to drive the PCA9685 directly.

With that in place, I hooked a red, a yellow, and a green LED up to
the PDA9695 board to give me some feedback channels.

There was the option here to design a custom PCB to hold both the
PCA9685 controller and the LEDs.  That might be suitable for a future
iteration, but for now the LEDs are hand-soldered through-hole
components on prototype board.  As and when we produce any more of
these, I can revisit that.

In terms of the software side, as with the keyboard support it made
sense to bundle up the thing driving the LEDs up separately to the
software doing the actual scanning, but for a slightly different
reason: if the scanner bit fails, I still want control over the LEDs
so I can blink my little red blinky light.  The code is [here](TODO);
I've not split it out to a separate project for the simple reason that
the bits of config that tell it what various patterns of lights mean
are super-specific to the business of being a scanner, and I haven't
got a clear picture in my head of how to separate that out well.

### Tying It All Together

So, with all those preparatory bits out of the way, onwards to the
main body of code.

On my first pass through, while I was trying to get the mk1 working, I
was using `darknet` itself at inference time, when trying to pull the
data out of the photo the scanner takes.  It turns out that, for
whatever reason, `darknet`'s inference mode was taking about a minute
to return any results when run on the Raspberry Pi, when the same
network and input image took 0.3 seconds to resolve on a laptop.  I
never figured out why: yes, there should be a difference, but that
wide a difference specifically on a network architecture designed for
use on edge devices was just odd.  I suspected that it was down to
`darknet` itself not being optimised for that architecture, rather
than the design.  At least, I hoped it was.

Fortunately, it proved straightforward to check.  OpenCV has a neural
network implementation called DNN which, it happens, is capable of
loading networks that darknet has trained.  Running the same network
and image through that library got the inference time down to 10
seconds.  Good, but still not quite good enough for practical use.

The network I initially trained was based on a YOLOv7 example, and had
an input network size of 416x416 pixels.  I thought that by reducing
the image size I might get some more speed, so I spun up another GPU
instance in AWS and trained a network with an input resolution of
224x224 pixels.

This worked better than I hoped: it trained faster than the 416x416
pixel version, and when transferred over to the raspberry pi, the
inference time, run through cv2.dnn, dropped to below three seconds.
Given the reduction by 75% in image size over the previous version,
for that to result in a run-time 25% of what it was is about the best
result I could have hoped for, and pushed the performance of the
scanner into the range of suitability for practical use.

The final piece of the puzzle, then, is a script to coordinate all the
parts I've built.  It's in [this directory](TODO).  In there you'll
find the main scanner service code which:

- waits for the button press
- takes a photo from the main camera when it's triggered
- processes the photo and passes it through the neural network
- extracts the interesting regions
- passes them to an OCR application to convert them to text
- pushes that text over USB to anything plugged in at the other end
- serves up a diagnostic page over HTTP so you can see what it's doing
- makes lights flash in visually stimulating and informative ways at
  various points along the way

There's also the accompanying systemd config to make the service start
up at boot time, as with the other services in this project.

### Developer Conveniences

#### Wifi

It's very useful to be able to connect to the scanner over the network
to diagnose what it's up to and to observe it working (or not).
However, in a lot of the places we work, it's not possible to connect
arbitrary raspberry pi's to the wifi to allow that to work.  Looking
at you, GovWifi.[^2]

It turns out that there's a fairly simple alternative, and that's for
the scanner to run its own access point.  With the right
configuration, the scanner presents itself as a hotspot that you can
connect to, with no further connectivity onwards to the internet but
enough of a network to allow you as a developer to connect to the
scanner and to do what you need to do.

[This directory](TODO) contains the scripts which will configure any
old raspberry pi to do this.  You can switch between access point and
ordinary network client mode (with a reboot, but that's fine for now)
and as long as you do that switch before you leave somewhere with
friendly wifi, all is well.

I'll need to revisit this as and when we have more devices in the same
location.  Having each one advertise its own AP isn't ideal in that
situation; I can see that I might well want them to join a specific
debugging AP run from a separate device.  But for now, it works.

#### Test screens

If the purpose of the scanner is to inject data into the hospital PAS
screen, it's useful to be able to demonstrate what that would look
like.  [This directory](TODO) contains a very straightforward HTML
mockup of the patient search screen of a hypothetical PAS, using the
[NHS Frontend Toolkit](TODO) to make it look good.  It's served over
the local network when the scanner is running so if you want to demo
it, you can.

## Author

Alex Young <alex.young12@nhs.net>


[^1]: There is a horrible, no good, very bad problem here that I am
    aware of but haven't yet corrected.  The name generator that I
    used for this was very... white.  I might very well have trained
    this system to be very good at identifying, for instance, "Jeff
    Smith" but extremely unreliable at picking out a "Mohinder Singh"
    or a "Jo Ng".  What I *hope* is that the model has learned that
    what matters is *where* letters are, not *what* they are, but this
    really, really needs testing - or better, just coming back and
    redoing once I can identify a much better source of training data
    than I had at the time.

[^2]: I'm probably being unfair.  It's not unlikely that this can be
    made to work if you know the right combination of settings, but I
    spent an afternoon poking at it with no luck.  And even if I *had*
    managed to get the scanner onto GovWifi, it still wouldn't be
    accessible to a laptop sat next to it because the network is
    designed (quite rightly) to segregate clients.
