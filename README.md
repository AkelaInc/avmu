
# AVMU Interface

Python 3 interface to AKELA Inc's vector meaurement units.

[Complete API Documentation here](https://akelainc.github.io/avmu/index.html)

Quickstart:

    import avmu

    AVMU_IP_ADDRESS = "192.168.1.219"
    HOP_RATE        = "HOP_15K"
    START_F         = 250
    STOP_F          = 2100
    NUM_POINTS      = 1024
    SWEEP_COUNT     = 100

    device = avmu.AvmuInterface()
    device.setIPAddress(AVMU_IP_ADDRESS)
    device.setIPPort(1027)
    device.setTimeout(500)
    device.setMeasurementType("PROG_ASYNC")

    device.initialize()

    device.setHopRate(HOP_RATE)
    device.addPathToMeasure('AVMU_TX_PATH_0', 'AVMU_RX_PATH_1')

    device.utilGenerateLinearSweep(startF_mhz=START_F, stopF_mhz=STOP_F, points=NUM_POINTS)

    # Get the freqency plan that utilGenerateLinearSweep calculated given the
    # hardware constraints.
    frequencies = device.getFrequencies()

    # Arm the device
    device.start()

    sweeps = []

    # Tell the AVMU to start asynchronous acquisitions.
    device.beginAsync()

    # Consume asynchronously generated frequency sweeps
    for _ in range(count):

        device.measure()
        sweep_data = device.extractAllPaths()
        sweeps.append(sweep_data)
        print("Acquired sweep (%s)" % (len(sweeps), ))

    # Stop the asynchronous acquisition
    device.haltAsync()

    # Finally, disarm the acquisition.
    device.stop()


Significantly more comprehensive examples are included in `demo-simple.py` and `demo-threaded.py`.

 - `demo-simple.py` shows how to properly convert acquired frequency domain data into time-domain 
   data, for extracting meaningful range profiles. It also includes a waterfall plot for viewing
   motion the returned data, if desired.
 - `demo-threaded.py` implements a much more robust, error tolerant client for the AVMU, with proper
   handling for the various way the network connection can hiccup.

### Usage:

If you clone this repository, the examples can be run directly, as the `avmu` package is present 
in the repository as well. However, for external projects, this depends on you manually placing
the `avmu` directory in the root of any project that would like to use it.

Alternatively, `avmu` is also available in PyPi, so `pip install avmu` will make the `avmu`
interface package available globally. At that point, either of the example files can be run
from any location.



## Changes:

0.0.11
 - Add extra setup classifiers that indicate MacOS/Linux support (whoops!)

0.0.10
 - This changeset primarily adds (preliminary) support for MacOS.
   There are no internal changes to the AVMU library, it solely consists of adding support 
   for locating/loading MacOS DyLibs, and the associated (internal) build-process support 
   for compiling on MacOS.
   Additionally, the windows build environment was also updated to VC141 (VS2017). This 
   should not affect users of this library, as the C ABI is stable across versions.

0.0.9
 - The combo utils tool has been updated to include the transmitting AVMU in each combo tuple.
   This will require any software that uses `avmu.combo_utils` to be updated, but as that particular
   file is so-far undocumented, this is not regarded as a breaking change. This change is motivated
   entirely by internal use of the library.

0.0.8
 - Added linux x86_64 shared object. This `.so` was built on ubuntu 16.04, so it will likely work on 
   most debian variants.

0.0.7
 - Minor DLL lookup improvements. Added linux armv7l shared object (e.g. raspberry pi version). 

0.0.6
 - Re-enable RTTI in the DLL, so it stops exploding. Whoops, sorry about that.
 
0.0.5
 - `utilPingUnit()` now takes an optional parameter to specify the number of retry attemps 
   for the ping.
 - Default timeout library-wide set to 100 milliseconds. Previously, it was 1000 milliseconds
   (and mis-documented as being 150). 1000 ms  doesn't make much sense in the context of the hardware, 
   which cannot (generally) perform blocking operations at all. As such, it *can't* take longer 
   then a millisecond or two to respond, if it received a message at all. 

0.0.4:
 - Improved return of `getHardwareDetails()` call to include hardware feature flags,   
   which makes determining what a remote AVMU can do easier then just trying to   
   turn on assorted features and seeing if you get errors.
 - Fixed typo in the reported versions in `setup.py` to include python 3.4.

0.0.3:
 - Initial Release






