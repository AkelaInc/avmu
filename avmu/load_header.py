

import os.path
import sys
import re

# THIS IS HORRRRRRRIIIIBBBBBBLLLEEEEE
# It works, though. -cw
HEADER_ROOT = os.path.abspath(os.path.join(__file__, "../../../../dlls/"))

AVMU_HEADER = os.path.join(HEADER_ROOT, "avmudll", "akela_avmu_dll.h")
VNA_HEADER   = os.path.join(HEADER_ROOT, "vnadll", "akela_vna_dll.h")
COMM_HEADER  = os.path.join(HEADER_ROOT, "dll_common", "dll_common.h")

def replace_preprocessor(in_header, no_declspec, cpp=False, htype=None):
	'''
	Join and rewrite the application headers so they're in a format that cffi can
	handle.

	This mostly involves a BUNCH of REALLY horrible string parsing hackery.
	'''
	conditional_split = re.compile(r"// <<<<<< CONDITIONAL START \(do not change this line\!\)|// \(do not change this line\!\) CONDITIONAL END >>>>>>>>")
	if conditional_split.search(in_header):
		pre, dll_def, post = re.split(r"// <<<<<< CONDITIONAL START \(do not change this line\!\)|// \(do not change this line\!\) CONDITIONAL END >>>>>>>>", in_header)
		in_header = pre + post
		dll_def = ""

	in_header = in_header.replace("CONDITIONAL_EXTERN", "")

	if htype == "avmu":
		in_header = in_header.replace("xxxDLL_API",   "AVMUDLL_API")
	elif htype == "vna":
		in_header = in_header.replace("xxxDLL_API",   "VNADLL_API")
		pass
	elif htype is None:
		pass
	else:
		raise ValueError("Invalid header type: '%s'" % htype)

	if no_declspec:
		# print("Doing no __declspec generation")
		in_header = in_header.replace("AVMUDLL_API", "__declspec(dllimport)")
		in_header = in_header.replace("VNADLL_API",   "__declspec(dllimport)")
		in_header = in_header.replace("xxxDLL_API",   "__declspec(dllimport)")
		in_header = in_header.replace("__declspec(dllimport)", "")
	else:
		# print("Doing __declspec generation")
		in_header = in_header.replace("AVMUDLL_API", "__declspec(dllimport)")
		in_header = in_header.replace("VNADLL_API",   "__declspec(dllimport)")
		in_header = in_header.replace("xxxDLL_API",   "__declspec(dllimport)")

	if not cpp:
		in_header = re.sub("// <<<<<< CPP WRAP START.*?CPP WRAP END >>>>>>>>", "", in_header, flags=re.DOTALL)
		in_header = in_header.replace(" = 5", "")    # Default arguments break the parser
		in_header = in_header.replace(" = 0", "")    # Default arguments break the parser
		in_header = in_header.replace(" = true", "") # Default arguments break the parser
		in_header = in_header.replace(" = NULL", "") # Default arguments break the parser

	in_header = re.sub("// <<<<<< SNIP START.*?SNIP END >>>>>>>>", "", in_header, flags=re.DOTALL)

	lines = []
	if not cpp:
		for line in in_header.split("\n"):
			if line.strip().startswith("#"):
				continue
			lines.append(line)

		in_header = "\n".join(lines)

	return in_header, dll_def

def assemble_header(main_header, common_header, output_path, no_declspec=True, cpp=False, header_name="__AKELA_DLL_HEADER", htype=None):
	mh = open(main_header).read()
	ch = open(common_header).read()

	# print(mh)
	# print(ch)

	mh, dll_def   = replace_preprocessor(mh, no_declspec, cpp, htype)
	ch, dummy_def = replace_preprocessor(ch, no_declspec, cpp, htype)

	pre, dummy, post = re.split("// <<<<<< INCLUDE START|INCLUDE END >>>>>>>>", mh)

	agg_h = pre + ch + post
	if not no_declspec:
		agg_h = """
#ifndef {hname}
#define {hname}
		""".format(hname=header_name) + agg_h + """
#endif

		"""

	splice_key = r"// <<<<<< SPLICE_POINT (do not change this line!) >>>>>>"
	if splice_key in agg_h and not no_declspec:
		# print("")
		# print("")
		# print("")
		# print("Splice point!")
		# print(dll_def)
		# print("")
		# print("")
		# print("")
		agg_h = agg_h.replace(splice_key, dll_def)

	dpath = os.path.split(output_path)[0]
	if not os.path.exists(dpath):
		os.makedirs(dpath)
	print("Writing to filepath: ", output_path)
	with open(output_path, "w") as fp:
		fp.write(agg_h)
	return agg_h



def load():
	header_root = os.path.join(os.path.dirname(__file__), "headers")

	try:
		agg_avmu = assemble_header(
				main_header   = AVMU_HEADER,
				common_header = COMM_HEADER,
				output_path   = os.path.join(header_root, "avmu_header_agg.h")
			)
		_        = assemble_header(
				main_header   = AVMU_HEADER,
				common_header = COMM_HEADER,
				output_path   = os.path.join(header_root, "avmu_header_agg_c.h"),
				no_declspec   = False,
				cpp           = True,
				header_name   = "__AKELA_AVMU_DLL_HEADER", htype='avmu'
			)
		_        = assemble_header(
				main_header   = VNA_HEADER,
				common_header = COMM_HEADER,
				output_path   = os.path.join(header_root, "vna_header_agg_c.h"),
				no_declspec   = False,
				cpp           = True,
				header_name   = "__AKELA_VNA_DLL_HEADER", htype='vna'
			)
	except FileNotFoundError:

		fdir = os.path.dirname(os.path.abspath(__file__))
		loc_header = os.path.join(fdir, "headers", "avmu_header_agg.h")

		if getattr(sys, 'frozen', False):
			# we are running in a |PyInstaller| bundle
			frozenheader = os.path.join(sys._MEIPASS, 'avmu_header_agg.h')
			agg_avmu = open(frozenheader).read()

		elif os.path.exists(loc_header):
			# Allow running from source when outside the development directory structure.
			agg_avmu = open(loc_header).read()
		else:
			raise
	return agg_avmu

