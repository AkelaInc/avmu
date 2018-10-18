
import sys

from . import dll_loader
from . import avmu_library

def header_update():

	ffi, dll = dll_loader.load_ffi_interface()


def dispatch(mode, args):
	funcs = {
		'gen_headers' : header_update
	}

	if mode in funcs:
		funcs[mode](*args)
	else:
		print("Error! No function matching '%s'!" % (mode))

def usage():
	print("Avmu testing widget")
	print("Usage: python(3) -m avmu <mode> [args]")
	print("")
	print("'Modes:")
	print("	gen_headers	- Regenerate headers from the library sources (Only useful for development)")

def go():
	print("AVMU CLI Test")
	if len(sys.argv) == 1:
		usage()
		return
	if len(sys.argv) > 1:
		mode, args = sys.argv[1], sys.argv[2:]
		dispatch(mode, args)


if __name__ == '__main__':
	go()

