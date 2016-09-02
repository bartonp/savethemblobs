#!/usr/bin/env python
#
# savethemblobs.py
#   A simple script to grab all SHSH blobs from Apple that it's currently signing to save them locally and on Cydia server.
#   And now also grabs blobs already cached on Cydia and iFaith servers to save them locally.
#
# Copyright (c) 2013 Neal <neal@ineal.me>
#
# examples:
#   savethemblobs.py 1050808663311 iPhone3,1
#   savethemblobs.py 0x000000F4A913BD0F iPhone3,1 --overwrite
#   savethemblobs.py 1050808663311 n90ap --skip-cydia --skip-ifaith

import sys, os, argparse
import requests
import json
import gzip
import md5
from ineal import INeal
import functools

__version__ = '1.0'

USER_AGENT = 'savethemblobs/%s' % __version__
ineal = INeal.Instance()

def firmwares_being_signed(device):
	return ineal.get_firmware_for_device(device)



def main(args = None):

	if not args:
		return

	if not os.path.exists(args.save_dir):
		os.makedirs(args.save_dir)

	print 'Fetching firmwares Apple is currently signing for {}'.format(args.device)
	device = firmwares_being_signed(args.device)

	if not device:
		print 'ERROR: No firmwares found! Invalid device.'
		return 1

	board = device['board']
	for f in device['firmwares']:
		url = 'https://api.ipsw.me/v2/{}/{}/info'.format(board, f['build'])
		r = requests.get(url)
		data = json.loads(r.text)[0]

		download_path = os.path.abspath(args.save_dir)
		file_path = os.path.join(download_path, data['url'].rsplit('/',1)[-1])

		print "Downloading {} for {}".format(data['version'], data['device'])
		print "  Filesize: {} bytes".format(data['filesize'])
		print "       MD5: {}".format(data['md5sum'])

		if os.path.isfile(file_path):
			m = md5.new()
			with open(os.path.join(file_path), 'r') as ipsw_file:
				for chunk in iter(functools.partial(ipsw_file.read, 4096), b''):
					m.update(chunk)

			if m.hexdigest() == data['md5sum']:
				print "            Download Skipped due to MD5 match on existing file\n"
				continue
			os.remove(file_path)


		ispw_r = requests.get(data['url'], stream=True)
		with open(os.path.join(file_path), 'wb') as ispw_file:
			for chunk in ispw_r.iter_content(chunk_size=1024):
				ispw_file.write(chunk)
		ispw_r.close()
		print "            File downloaded."

		print ""
	return 0

if __name__ == '__main__':
	sys.exit(main())
