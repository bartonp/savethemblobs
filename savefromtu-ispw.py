#!/usr/bin/env python
# savefromtu.py - save blobs etc from a device stored in tinyumbella's known device plist files

import os
import argparse
import savethemispw
import gzip
import plistlib

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--save-dir', help='local dir for saving blobs (default: ~/.shsh)', default=os.path.join('.', 'ispw'))
	parser.add_argument('--tu-path', help='Point to the Tinyumbrella config path (default ~/.tu)', default=os.path.join('~', '.tu'))
	args = parser.parse_args()
	return args

class Device(object):
	__data = {}
	__file = ""

	def __init__(self, f=''):
		super(Device, self).__init__()
		self.__file = f

	def connect(self):
		g = gzip.open(self.__file, 'rb')
		self.__data = plistlib.readPlistFromString(g.read())
		g.close()

	def get_value(self, name=''):
		if name in self.__data:
			return self.__data[name]
		return None

def get_tiny_umbrella_devices(tu_path):
	tu_path = os.path.join(os.path.expanduser(tu_path), '.known_devices')
	devices = []
	for dirname, dirs, files in os.walk(tu_path):
		for f in files:
			devices.append(Device(os.path.join(dirname, f)))
	return devices


def main():
	args = parse_args()
	devices = get_tiny_umbrella_devices(args.tu_path)

	for device in devices:
		device.connect()

		identifier = device.get_value(name=u'ProductType')
		ecid = device.get_value(name=u'UniqueChipID')

		print "Device: {} [{}]".format(ecid, identifier)

		args = parse_args()
		args.device = identifier

		savethemispw.main(args)
		print ""


if __name__ == '__main__':
	main()
