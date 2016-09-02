#!/usr/bin/env python
# savefromtu.py - save blobs etc from a device

import os
import argparse
import requests
import savethemblobs
import gzip
import plistlib

def get_user_friendly_name(identifier):
	url = 'http://api.ios.icj.me/v2/%s/latest/name' % (identifier)
	r = requests.get(url, headers={'User-Agent': savethemblobs.USER_AGENT})
	return r.text

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--save-dir', help='local dir for saving blobs (default: ~/.shsh)', default=os.path.join(os.path.expanduser('~'), '.shsh'))
	parser.add_argument('--overwrite', help='overwrite any existing blobs', action='store_true')
	parser.add_argument('--overwrite-apple', help='overwrite any existing blobs (only from Apple)', action='store_true')
	parser.add_argument('--overwrite-cydia', help='overwrite any existing blobs (only from Cydia)', action='store_true')
	parser.add_argument('--overwrite-ifaith', help='overwrite any existing blobs (only from iFaith)', action='store_true')
	parser.add_argument('--no-submit-cydia', help='don\'t submit blobs to Cydia server', action='store_true')
	parser.add_argument('--skip-cydia', help='skip fetching blobs from Cydia server', action='store_true')
	parser.add_argument('--skip-ifaith', help='skip fetching blobs from iFaith server', action='store_true')
	parser.add_argument('--tu-path', help='Point to the Tinyumbrella config path (default ~/.tu)', default=os.path.join('~', '.tu'))
	return parser.parse_args()

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
		print identifier, ecid
		#print "Device: {1} [{1}]".format(device.get_value(name='DeviceName').encode('ascii'), identifier)

		args = parse_args()
		args.device = identifier
		args.ecid = str(ecid)
		args.overwrite = False
		args.no_submit_cydia = True
		args.skip_cydia = True
		args.skip_ifaith = True

		savethemblobs.main(args)
		print ""

if __name__ == '__main__':
	main()
