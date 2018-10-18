# ######################################################################### #
#  dll_loader.py	--	Python module wrapping AVMUDLL/VNADLL				#
# 																			#
#  	Adapted from /libbytecode/vnadll/akela_vna_dll.h							#
# 																			#
# 	Author: Connor Wolf <cwolf@akelainc.com>								#
# 																			#
# ######################################################################### #


import os.path
import platform
import sys
import traceback
import shutil


def get_search_paths():
	''' Build a list of search paths where we should look for the
	AVMU DLL.

	'''
	locations = []
	loc = os.path.dirname(os.path.abspath(__file__))
	up = os.path.abspath(os.path.join(loc, "../"))
	upp = os.path.abspath(os.path.join(up, "../"))
	build_dir_dbg1 = os.path.abspath(os.path.join(loc, "../../../x64/Debug/"))
	build_dir_dbg2 = os.path.abspath(os.path.join(loc, "../../../Out/x64/Debug/"))
	build_dir_rls1 = os.path.abspath(os.path.join(loc, "../../../Out/x64/Release/"))
	build_dir_rls2 = os.path.abspath(os.path.join(loc, "../../../Out/x64/ReleaseWProgram/"))
	build_dir_rls3 = os.path.abspath(os.path.join(loc, "../../../../../Out/x64/ReleaseWProgram/"))
	build_dir_rls4 = os.path.abspath(os.path.join(loc, "../../../../../Out/x64/Release/"))
	locations.append(build_dir_dbg1)
	locations.append(build_dir_dbg2)
	locations.append(build_dir_rls1)
	locations.append(build_dir_rls2)
	locations.append(build_dir_rls3)
	locations.append(build_dir_rls4)
	locations.append(loc)
	locations.append(upp)
	locations.append(up)



	split_on = {"Linux" : ":", "Windows" : ";"}
	split = os.environ['PATH'].split(split_on[platform.system()])

	if getattr(sys, 'frozen', False):
		# we are running in a |PyInstaller| bundle
		locations.append(sys._MEIPASS)

	# Validate and canonize the various paths
	split = [os.path.abspath(item) for item in split if os.path.exists(item)]

	ret = locations+split
	return ret

def check_copy_to_local(fq_dll_path, dll_name):
	lib_dir = os.path.dirname(os.path.abspath(__file__))

	# Dll is in the library directory. Just use it as-is.
	if fq_dll_path.startswith(lib_dir):
		return fq_dll_path

	print("DLL is not located in the library directory. Attempting to copy it there")
	to_path = os.path.join(lib_dir, dll_name)

	try:
		shutil.copy(fq_dll_path, to_path)
		print("Library copied into tree. Path: %s" % (to_path))
		return to_path
	except Exception:
		print("Failed to move dll into library directory!")
		print("Target location: %s" % (to_path, ))
		print("DLL Location: %s" % (fq_dll_path, ))
		traceback.print_exc()
		return fq_dll_path

def find_dll():
	''' Search both the local working directory, and the
	system environment (`PATH`) for the DLL/SO.
	'''

	dll_lut = {"Linux" : "libavmu.so", "Windows" : "avmudll.dll"}

	plat = platform.system()

	if plat in dll_lut:
		dll_name = dll_lut[plat]
	else:
		raise RuntimeError("Unknown platform: '%s'" % platform.system())

	locations = get_search_paths()


	for location in locations:
		fq_dll_path = os.path.join(location, dll_name)
		if os.path.exists(fq_dll_path):
			print("Found avmu dll at path: '{}'".format(fq_dll_path))
			return check_copy_to_local(fq_dll_path, dll_name)
	raise ValueError("Could not find DLL/SO! Searched paths: \n	- %s" % "\n	- ".join(locations))


STATIC_FFI = None
STATIC_LIB = None

def load_ffi_interface():
	'''
	Load and return the FFI library instance, and DLL interface to the avmu DLL.

	return value is a 2-tuple (ffi_lib, dll_handle)
	'''

	# We have to use globals or some sort of persistent state here, because if
	# we load the DLL twice, it'll create two typedef classes for all the DLL objects,
	# which will then fail to interoperate.
	global STATIC_FFI
	global STATIC_LIB
	if STATIC_FFI is not None and STATIC_LIB is not None:
		return STATIC_FFI, STATIC_LIB

	dll_path = find_dll()

	from . import load_header
	from cffi import FFI


	ffi = FFI()
	headers = load_header.load()

	ffi.cdef(headers)
	lib = ffi.dlopen(dll_path)

	print("Loaded library version: ", ffi.string(lib.versionString()).decode("utf-8"))

	STATIC_FFI = ffi
	STATIC_LIB = lib

	return ffi, lib

