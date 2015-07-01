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

#File handling
import os.path
import json

#Global modes
shutdown = False
debugMode = False
silentMode = False

#Global variables
dev = 0
interface = 0
endpoint = 0

#Config variables
configFile = "pyRC102.conf"
configJson = 0
usbReceiverVid = 5242
usbReceiverPid = 57369

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

	if debugMode:
		print("Loading USB.")

	if debugMode:
		print("Finding USB receiver.")
	# decimal vendor and product values
	#dev = usb.core.find(idVendor=1118, idProduct=1917)
	dev = usb.core.find(idVendor=usbReceiverVid, idProduct=usbReceiverPid)
	# or, uncomment the next line to search instead by the hexidecimal equivalent
	#dev = usb.core.find(idVendor=0x147a, idProduct=0xe019)

	# first endpoint
	interface = 0
	endpoint = dev[0][(0,0)][0]

	# if the OS kernel already claimed the device, which is most likely true
	# thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
	if dev.is_kernel_driver_active(interface) is True:
		if debugMode:
			print("Kernel driver is active, detach it.")
		# tell the kernel to detach
		dev.detach_kernel_driver(interface)
		# claim the device
		usb.util.claim_interface(dev, interface)
	else:
		if debugMode:
			print("Kernel driver is not active.")

def threadReceiveLoop():
	collected = 0
	while not shutdown :
		try:
			data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
			collected += 1
			print data
		except usb.core.USBError as e:
			if debugMode:
				print("usb.core.USBError:")
				print(e)
			data = None
			if e.args == ('Operation timed out',):
				if debugMode:
					print("Operation timed out, continue.")
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
	print ("--config : filename of the configfile to use")
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
		opts, args = getopt.getopt(sys.argv[1:],"c:hds",["config=","help", "debug", "silent"])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(1)

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
		elif o in ("-c", "--config"):
			global configFile
			configFile = a
		else:
			raise Exception("Unhandled option %s." % o)

def readConfig():
	if debugMode:
		print("Checking if config file %s exist." % configFile)
	if not os.path.exists(configFile):
		print("Config file %s don't exist." % configFile)
		print("An example config file should be provided under the filename: pyRC102.conf.sample")
		sys.exit(2)

	if debugMode:
		print("Opening config file.")
	global configJson
	try:
		with open(configFile) as json_data_file:
			if debugMode:
				print("Reading JSON format.")
			configJson = json.load(json_data_file)
	except Exception as err:
		print("Couldn't read the config file as JSON-format.")
		print(err)
		sys.exit(3)
	if debugMode:
		print("Config data:")
		print(configJson)

	global usbReceiverVid
	try:
		usbReceiverVid = configJson["usbreceiver"]["vid"]
	except Exception as err:
		if debugMode:
			print("Couldn't read usbreceiver vid.")
			print(err)

	global usbReceiverPid
	try:
		usbReceiverPid = configJson["usbreceiver"]["pid"]
	except Exception as err:
		if debugMode:
			print("Couldn't read usbreceiver pid.")
			print(err)

	if not isinstance( usbReceiverVid, ( int, long ) ):
		if debugMode:
			print("usbReceiverVid is not an integer, try convert it.")
		#With the 0x prefix, Python can distinguish hex and decimal automatically
		usbReceiverVid = int(usbReceiverVid, 0)

	if not isinstance( usbReceiverPid, ( int, long ) ):
		if debugMode:
			print("usbReceiverPid is not an integer, try convert it.")
		#With the 0x prefix, Python can distinguish hex and decimal automatically
		usbReceiverPid = int(usbReceiverPid, 0)

	if debugMode:
		print("Parameter usbreceiver vid is %s." % usbReceiverVid)
		print("Parameter usbreceiver pid is %s." % usbReceiverPid)

if __name__ == '__main__':
	#Parse Arguments
	parseArgs()

	#Read config file
	readConfig()

	#Call Main-function
	main()

