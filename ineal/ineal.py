import requests
import json

def _check_all_firmwares(func):
	def funcwrapper(self, *args, **kwargs):
		if not self._signed_firmwares:
			self.get_all_firmwares_currently_signed()
		return func(self, *args, **kwargs)
	return funcwrapper

class INeal(object):
	__Instance = None

	@classmethod
	def Instance(cls, *args, **kwargs):
		if cls.__Instance is None:
			cls.__Instance = INeal(*args, **kwargs)
		return cls.__Instance

	def __init__(self):
		super(INeal, self).__init__()

		self.base_url = 'http://api.ineal.me'

		self.session = requests.Session()
		self.session.headers = {"User-Agent" : 'FromPython'}
		self._signed_firmwares = None
		self._cache = {}

	def get_all_firmwares_currently_signed(self):
		if not self._signed_firmwares:
			args = '/tss/all/includebeta'
			items = self.__response(args)
			self._signed_firmwares = json.loads(items)
		return self._signed_firmwares

	@_check_all_firmwares
	def get_firmware_for_device(self, device):
		if device in self._signed_firmwares:
			return self._signed_firmwares[device]
		return None


	def __response(self, args):
		url = "{}{}".format(self.base_url, args)
		r = self.session.get(url)
		return r.text


	def _request_cache(self, reqtype, board, build):
		if reqtype not in self._cache:
			self._cache[reqtype] = {}

		if board not in self._cache[reqtype]:
			self._cache[reqtype][board] = {}

		if build not in self._cache[reqtype][board]:
			args = '/tss/{}/{}/{}'.format(reqtype, board, build)
			data = self.__response(args)
			self._cache[reqtype][board][build] = data
		return self._cache[reqtype][board][build]


	def request_manifest(self, board, build):
		return self._request_cache('manifest', board, build)

	def request_restore_plist(self, board, build):
		return self._request_cache('restoreplist', board, build)

	def request_build_manifest(self, board, build):
		return self._request_cache('buildmanifest', board, build)

#if __name__ == "__main__":
#	i = INeal()
#	print i.get_firmware_for_device('iPod7,1')
#	print i.request_restore_plist('n102ap', '13G36')
#	print i.request_build_manifest('n102ap', '13G36')
