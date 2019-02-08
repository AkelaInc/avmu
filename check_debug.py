
import os


def check_dll(dll_path):

	with open(dll_path, "rb") as fp:
		dll_bin = fp.read()


	assert b"Private API mode" not in dll_bin, "DLL In package contains in-house testing symbols!"
	assert b"Debug DLL" not in dll_bin, "DLL In package appears to be built in debug mode!"

def update_docs():
	os.system('make html')
	os.system('cp -r ./build/html/* ./docs')



if __name__ == '__main__':
	check_dll("avmu/avmudll_amd64_win.dll")
	check_dll("avmu/libavmu_armv7l_linux.so")
	check_dll("avmu/libavmu_amd64_linux.so")
	check_dll("avmu/libavmu_amd64_macos.dylib")
	update_docs()
