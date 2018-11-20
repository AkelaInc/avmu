
import random
from . import avmu_library
from . import avmu_exceptions

def is_avmu_alive(target_ip, port=None):
	'''
	Context-free "Is there something at this IP" command.

	Uses a random port between 1050 and 1279, so multiple calls at the same time
	*should* be generally harmless, though if you're pinging the same unit the
	AVMU may get confused, and some of the ping responses may get lost.

	Functionally, the AVMU sends it's responses to the last IP address it received
	data from. Therefore, arbitrary UDP traffic can cause the AVMU to change where
	it's sending data.
	'''

	if port is None:
		port = random.randint(1050, 1279)

	device = avmu_library.AvmuInterface()
	device.setIPAddress(target_ip)
	device.setIPPort(port)
	device.setTimeout(100)

	try:
		device.utilPingUnit()
		return True
	except avmu_exceptions.Avmu_Exception:
		return False

def get_avmu_info(target_ip):
	'''
	Given an AVMU at a specified address, connect to it, and
	return it's hardware details.
	'''

	device = avmu_library.AvmuInterface()
	device.setIPAddress(target_ip)
	device.setIPPort(random.randint(1050, 1279))
	device.setTimeout(100)
	device.initialize()

	deets = device.getHardwareDetails()
	return deets


if __name__ == '__main__':
	import logging
	import sys
	import pprint
	# logging.basicConfig(level=logging.DEBUG)


	if len(sys.argv) >= 2:
		tgt = sys.argv[1]
		info = get_avmu_info(tgt)
		print("Avmu info: ")
		pprint.pprint(info)
	else:
		print("No Arguments!")


