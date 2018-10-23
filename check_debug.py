

with open("avmu/avmudll.dll", "rb") as fp:
	dll_bin = fp.read()


assert b"Private API mode" not in dll_bin, "DLL In package contains in-house testing symbols!"
assert b"Debug DLL" not in dll_bin, "DLL In package appears to be built in debug mode!"

