#!/usr/bin/env python
# -*- coding: utf-8 -*-

#USB-stuff needed
import usb.core
import usb.util

#Parsing arguments
import sys
import getopt
import threading

#Sigint
import signal

#Global variables
shutdown = False
debugMode = False
silentMode = False

dev = 0
interface = 0
endpoint = 0

def about():
	print("pyRC102Remote")
	print("=============")
	print("Listens to infrared codes from a remotecontrol through a receiver called RC102-809,")
	print("and converts it's signals, send them over to LIRC (a daemon for remotecontrols).")
	print("Read more about LIRC at http://www.lirc.org/")
	print("By Tim Gremalm, tim@gremalm.se, http://tim.gremalm.se")

def main():
	if not silentMode:
		print("Starting pyRC102")

	#Start listening for SIGINT (Ctrl+C)
	signal.signal(signal.SIGINT, signal_handler)

	initUSB()

	t = threading.Thread(target=threadReceiveLoop, args=())
	t.start()

	#Cause the process to sleep until a signal is received
	signal.pause()

	unloadUSB()

	if debugMode:
		print("Thread is closed, terminating process.")
	sys.exit(0)

def initUSB():
	global dev
	global interface
	global endpoint

	# decimal vendor and product values
	#dev = usb.core.find(idVendor=1118, idProduct=1917)
	dev = usb.core.find(idVendor=5242, idProduct=57369)
	# or, uncomment the next line to search instead by the hexidecimal equivalent
	#dev = usb.core.find(idVendor=0x147a, idProduct=0xe019)

	# first endpoint
	interface = 0
	endpoint = dev[0][(0,0)][0]

	# if the OS kernel already claimed the device, which is most likely true
	# thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
	if dev.is_kernel_driver_active(interface) is True:
		# tell the kernel to detach
		dev.detach_kernel_driver(interface)
		# claim the device
		usb.util.claim_interface(dev, interface)

def threadReceiveLoop():
	collected = 0
	attempts = 50
	while not shutdown :
		try:
			data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
			collected += 1
			print data
		except usb.core.USBError as e:
			data = None
			if e.args == ('Operation timed out',):
				continue

def unloadUSB():
	if debugMode:
		print("Unloading USB.")
	if debugMode:
		print("Releasing interface.")
	# release the device
	usb.util.release_interface(dev, interface)
	if debugMode:
		print("Reattach the device to the OS kernel.")
	# reattach the device to the OS kernel
	dev.attach_kernel_driver(interface)

def aboutAndUsage():
	about()
	usage()

def usage():
	print ("--help : shows this help")
	print ("--debug : shows all events")
	print ("--silent : keeps quiet")

def signal_handler(signal, frame):
	if not silentMode:
		print('SIGINT detected. Prepareing to shut down.')
	global shutdown
	shutdown = True

def parseArgs():
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hds",["help", "debug", "silent"])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)

	for o, a in opts:
		if o in ("-h", "--help"):
			aboutAndUsage()
			sys.exit(0)
		elif o in ("-d", "--debug"):
			global debugMode
			debugMode = True
		elif o in ("-s", "--silent"):
			global silentMode
			silentMode = True
		else:
			assert False, "unhandled option"

if __name__ == '__main__':
	#Parse Arguments
	parseArgs()

	#Call Main-function
	main()

