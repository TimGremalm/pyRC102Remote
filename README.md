# pyRC102Remote
a decoder for the IR-reciever RC102-809
Based on http://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack

## What does it do?
Listens to infrared codes from a remotecontrol through a receiver called RC102-809, and converts it's signals, send them over to LIRC (a daemon for remotecontrols). Read more about LIRC at http://www.lirc.org/

The RC102-809 is a generic circuit that many cheap brand rebrand in their own name. For instance my unit is a Trust - NB5100p (http://www.trust.com/en/all-products/14272-multimedia-remote-control-nb5100p).

## Requirements
* PyUSB - http://walac.github.io/pyusb/
* libusb - http://www.libusb.org/

## Configuration
Write your configfile based on pyRC102.conf.sample, name it pyRC102.conf.

Run dmesg to the VID (Vendor ID) and PID (Product ID). Make sure they are correct in the configfile.
Look for the description "Formosa Industrial Computin Formosa RC102-809 USB Remot".

The RC102-809 have:
VID 147a and PID e019

Start pyRC102 in debug-mode and listen to the signals from your remote.
```bash
sudo ./pyRC102.py --debug
```
Write down you signals in the config file.
Make sure to match up the ir-codes with the commands in your LIRC-config.

## Run
run with root-privileges:
```bash
sudo ./pyRC102.py
```

