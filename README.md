# pyRC102Remote
a decoder for the IR-reciever RC102-809
Based on http://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack

## What does it do?
Listens to infrared codes from a remotecontrol through a receiver called RC102-809, and converts it's signals, send them over to LIRC (a daemon for remotecontrols). Read more about LIRC at http://www.lirc.org/

The RC102-809 is a generic circuit that many cheap brands rebrand with their own name. For instance my unit is a Trust - NB5100p (http://www.trust.com/en/all-products/14272-multimedia-remote-control-nb5100p).
Other common names on the same unit is Conceptronic CMMRC, Wirtech Clic & Zap, Hama Remote Control for Windows Media Center, Tevion Computing Slim USB multi remote controller, Formosa IR 507, Formosa 21/ eDio 21.

## Requirements
* PyUSB - https://walac.github.io/pyusb/
* libusb - http://www.libusb.org/
* python-lirc-send - https://github.com/prcjac/python-lirc-send

## Configuration
Write your config file based on pyRC102.conf.sample, name it pyRC102.conf.

### Configure the dongle
To find the VID (Vendor ID) and PID (Product ID); run dmesg to find the latest pluged in device.  Look for the description "Formosa Industrial Computin Formosa RC102-809 USB Remot".

The RC102-809 have:
VID 147a and PID e019

### Configure LIRC
You can choose what ever config as you want to, pyRC102Remote will inject the commands into the socket and simulate signals from that remote.

Preferable a generic config like the mceusb.

Add the argument allow simulate to let lircd receive simulated IR-commands.
```conf
REMOTE_LIRCD_ARGS="--allow-simulate"
```
Example config can be found under lirc_config_sample.

### Configure the codes
To get the codes from your remote control, start pyRC102 in debug-mode.
Run with root-privileges to enable access to USB.
```bash
sudo ./pyRC102.py --debug
```
Write down the signals in the config file.
Press <kbd>CTRL</kbd>+<kbd>C</kbd> to exit.

For each code, write down coresponding sendmessage string from your LIRC-config.
Syntax for the sendmessage:
```conf
buttonCode Repeat buttonName RemotecontrolName
```
For example:
```conf
0000000000001bee 00 VolDown mceusb_hauppauge
```
## Test with LIRC
To test if your entered commands work with LIRC, run:
```bash
irw
```

## Install
Copy pyRC102 (LSB Init) to your init.d, make sure it's runable.
```bash
sudo cp pyRC102 /etc/init.d/
sudo chmod +x /etc/init.d/pyRC102
```

Edit the path /change/to/pyRC102installdir in /etc/init.d/pyRC102

Make it start up with the computer
```bash
sudo update-rc.d pyRC102 defaults
```

