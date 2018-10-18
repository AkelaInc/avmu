
import sys
import struct
import os

if sys.version_info < (3, 4):
    sys.exit('Sorry, Python < 3.4 is not supported')

if os.name != 'nt':
    sys.exit('Only windows installs are supported for PyPi installs. Please ' +
        'contact AKELA Inc for linux packages.')

if struct.calcsize("P") * 8 != 64:
    sys.exit("This interface requires 64 bit python!")


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name                          = "avmu",
    version                       = "0.0.3",
    author                        = "Connor Wolf, Akela Inc",
    author_email                  = "cwolf@akelainc.com",
    description                   = "Control interface and API for running Akela Vector Measurement Units.",
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/AkelaInc/avmu",
    packages                      = setuptools.find_packages(),
    python_requires               = ">=3.5",
    install_requires              = [
            'numpy',
            'cffi',
        ],
    include_package_data          = True,
    classifiers                   = [
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
    ],
)