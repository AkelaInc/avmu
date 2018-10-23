
import os


def check_dll():

	with open("avmu/avmudll.dll", "rb") as fp:
		dll_bin = fp.read()


	assert b"Private API mode" not in dll_bin, "DLL In package contains in-house testing symbols!"
	assert b"Debug DLL" not in dll_bin, "DLL In package appears to be built in debug mode!"

def update_docs():
	os.system('make html')
	os.system('cp -r ./build/html/* ./docs')



if __name__ == '__main__':
	check_dll()
	update_docs()
