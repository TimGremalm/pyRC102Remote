#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
import getopt
import threading
import usb.core
import usb.util
import os.path
import json
import numpy

#Global modes
shutdown = False
verboseMode = 1

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
	if verboseMode > 1:
		print("Starting pyRC102")

	#Start listening for SIGINT (Ctrl+C)
	signal.signal(signal.SIGINT, signal_handler)

	initUSB()

	t = threading.Thread(target=threadReceiveLoop, args=())
	t.start()

	#Cause the process to sleep until a signal is received
	signal.pause()

	unloadUSB()

	if verboseMode > 2:
		print("Thread is closed, terminating process.")
	sys.exit(0)

def initUSB():
	global dev
	global interface
	global endpoint

	if verboseMode > 1:
		print("Loading USB.")

	if verboseMode > 2:
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
		if verboseMode > 2:
			print("Kernel driver is active, detach it.")
		# tell the kernel to detach
		dev.detach_kernel_driver(interface)
		# claim the device
		usb.util.claim_interface(dev, interface)
	else:
		if verboseMode > 2:
			print("Kernel driver is not active.")

def threadReceiveLoop():
	while not shutdown :
		try:
			data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)

			#Convert array to list
			data = numpy.array(data).tolist()

			if verboseMode > 1:
				dataHex = []
				for segment in data:
					dataHex.append(format(segment, '0>2X'))
				print("Data received Dec: {} Hex: {}".format(str(data), str(dataHex)))
			compareSignalToCode(data)
		except usb.core.USBError as e:
			if verboseMode > 2:
				print("usb.core.USBError:")
				print(e)
			data = None
			if e.args == ('Operation timed out',):
				if verboseMode > 2:
					print("Operation timed out, continue.")
				continue

def compareSignalToCode(signal):
	for code in configJson["codes"]:
		#Compare recieved code to the sored codes in the config file
		if code["code"] == signal:
			if verboseMode > 0:
				print("Matched against config {}".format(code["sendmessage"]))

def unloadUSB():
	if verboseMode > 1:
		print("Unloading USB.")
	if verboseMode > 2:
		print("Releasing interface.")
	# release the device
	usb.util.release_interface(dev, interface)
	if verboseMode > 2:
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
	if verboseMode > 0:
		print(' SIGINT detected. Prepareing to shut down.')
	global shutdown
	shutdown = True

def parseArgs():
	try:
		opts, args = getopt.getopt(sys.argv[1:],"c:hdsv",["config=","help", "debug", "silent", "verbose"])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(1)

	for o, a in opts:
		global verboseMode
		if o in ("-h", "--help"):
			aboutAndUsage()
			sys.exit(0)
		elif o in ("-s", "--silent"):
			verboseMode = 0
		elif o in ("-d", "--debug"):
			verboseMode = 2
		elif o in ("-v", "--verbose"):
			verboseMode = 3
		elif o in ("-c", "--config"):
			global configFile
			configFile = a
		else:
			raise Exception("Unhandled option %s." % o)

def readConfig():
	if verboseMode > 2:
		print("Checking if config file %s exist." % configFile)
	if not os.path.exists(configFile):
		print("Config file %s don't exist." % configFile)
		print("An example config file should be provided under the filename: pyRC102.conf.sample")
		sys.exit(2)

	if verboseMode > 2:
		print("Opening config file.")
	global configJson
	try:
		with open(configFile) as json_data_file:
			if verboseMode > 2:
				print("Reading JSON format.")
			configJson = json.load(json_data_file)
	except Exception as err:
		print("Couldn't read the config file as JSON-format.")
		print(err)
		sys.exit(3)
	if verboseMode > 2:
		print("Config JSON data:")
		print(configJson)

	global usbReceiverVid
	try:
		usbReceiverVid = configJson["usbreceiver"]["vid"]
	except Exception as err:
		if verboseMode > 0:
			print("Couldn't read usbreceiver vid.")
			print(err)

	global usbReceiverPid
	try:
		usbReceiverPid = configJson["usbreceiver"]["pid"]
	except Exception as err:
		if verboseMode > 0:
			print("Couldn't read usbreceiver pid.")
			print(err)

	if not isinstance( usbReceiverVid, ( int, long ) ):
		if verboseMode > 2:
			print("usbReceiverVid is not an integer, try convert it.")
		#With the 0x prefix, Python can distinguish hex and decimal automatically
		usbReceiverVid = int(usbReceiverVid, 0)

	if not isinstance( usbReceiverPid, ( int, long ) ):
		if verboseMode > 2:
			print("usbReceiverPid is not an integer, try convert it.")
		#With the 0x prefix, Python can distinguish hex and decimal automatically
		usbReceiverPid = int(usbReceiverPid, 0)

	if verboseMode > 1:
		print("Parameter usbreceiver vid is %s." % usbReceiverVid)
		print("Parameter usbreceiver pid is %s." % usbReceiverPid)

	#Loop through codes
	for i, code in enumerate(configJson["codes"]):
		for j, segment in enumerate(code["code"]):
			#Make sure code segment is an integer
			if not isinstance( segment, ( int, long ) ):
				#With the 0x prefix, Python can distinguish hex and decimal automatically
				configJson["codes"][i]["code"][j] = int(segment, 0)

	if verboseMode > 2:
		print("List of codes from config file.")
		for code in configJson["codes"]:
			print(code)

if __name__ == '__main__':
	#Parse Arguments
	parseArgs()

	#Read config file
	readConfig()

	#Call Main-function
	main()

