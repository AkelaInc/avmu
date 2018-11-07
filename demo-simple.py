
import time
import numpy as np
import matplotlib.pyplot as plt

import avmu

'''
This is a small example that demonstrates how to use the AKELA AVMU to
acquire range data, in a maximally simple manner. The actual AVMU interface
code does not do any error handling, but for short acquisitions, this is
generally fine.

The structure is minimal:

 - get_sweeps() acquires a set of frequency-domain data
 - plot_sweeps() handles converting the data to time-domain, and then does some plotting.

 - phase_correct_ifft() is the core of how to convert the AVMU's return data (which
    is frequency-domain data) to time-domain data that is useful for ranging
    purposes.


'''


AVMU_IP_ADDRESS = "192.168.1.223"

HOP_RATE        = "HOP_15K"
START_F         = 250
STOP_F          = 2100

NUM_POINTS      = 1024
SWEEP_COUNT     = 100

# Cable delays are 0.65 nanoseconds each way (tx cable + rx cable)
CABLE_DELAYS = 0.65 * 2

def log_mag(inarr):
	return 20 * np.log10(np.absolute(inarr))


def phase_correct_ifft(data, start_f, stop_f, npts, cable_delays, fft_window=np.hanning):
	'''
	To properly convert the frequency domain data returned by the AVMU into meaninful
	time-domain data, we have to do a little bit of work.

	Basically, the AVMU returns a set of I/Q samples for the return signal at each
	measured frequency point. These can be converted to time-domain magnitude/phase
	data using an inverse FFT.

	However, you can't directly just shove the AVMU data into a iFFT, as the AVMU
	data does not start at 0 Hz. Therefore, we have to zero pad the beginning
	of the dataset so the frequency points returned by the AVMU are properly
	aligned in the iFFT input.


	Basically:

		AVMU Output
		                    V Sweep Start    V Sweep End
		                    |  < n points >  |

		As we know the start frequency, stop frequency, and the number of points, we
		can therefore calculate the effective step per frequency:
		 (stop freq - start freq)  n points.

		Then, we can calculate how many points we need to pad the beginning of the FFT with:

		(start freq - 0) / step-per-point = zero-padding

		We then wind up with:
		V 0 hz              V Sweep Start    V Sweep End
		|  <zero padding>   |  < n points >  |

		As FFT calculations are generally MUCH more efficent when the FFT (or
		iFFT) length is a size that is a power of two, we then zero pad the
		end of the array as well, to make the overall point size equal to
		the next-nearest-larger power of two:
		V 0 hz              V Sweep Start    V Sweep End            V 2^n pts
		|  <zero padding>   |  < n points >  |    < zero padding    |

		We can then perform a iFFT and get meanignful results.

	The output of the iFFT is complex time-domain data. The time-step per bin
	is a function of the frequency-step per bin in the input. Basically:
	time_step = 1 / (frequency_step * fft_size * 2).

	Finally, since the data is now in the time-domain, we shift the time axis by
	the length of the delays in the cables, to get the real distance.

	'''

	data_len = data.shape[0]

	# Apply windowing (needs to be an elementwise multiplication)
	data = np.multiply(data, fft_window(data_len))

	# Pad the start of the array for phase-correctness, and
	# the end to make the calculation a power of N
	step_val = abs(start_f - stop_f) / npts
	start_padding = max(int(start_f/step_val), 0)

	startsize = start_padding + data_len

	sizes = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65535]
	start_idx   = 0
	output_size = 0
	while output_size < startsize and start_idx < len(sizes):
		output_size = sizes[start_idx]
		start_idx += 1

	end_padding = max(output_size - startsize, 0)

	# Default padding value is "0"
	arr = np.pad(data, (start_padding, end_padding), mode='constant')

	# Since we acquire directly as frequency domain, and we want to convert
	# back to time-domain, we use a iFFT, rather then a normal FFT
	fft_data = np.fft.ifft(arr)

	# Chop off the negative time component (we don't care about it here)
	# Someone doing fancier stuff could put it back.
	fft_data = fft_data[:output_size//2]
	fft_data = np.absolute(fft_data)

	if start_f == stop_f:
		return fft_data, np.array(range(fft_data.shape[0]))

	pts = np.array(range(fft_data.shape[0]))

	# Convert to hertz
	step_val = step_val * 1e6

	# And then to time
	pts = pts * (1 / (len(pts) * step_val * 2))

	# Finally to nanoseconds
	pts = pts * 1e9

	# And then we subtract off the cable delays.
	# This will shift the zero time to a negative value, but that's fine, since
	# we're treating the antenna plane as the "zero" time
	pts = pts - cable_delays

	return fft_data, pts


def waterfall_plot(y_axis_set, x_axis, time_per_frame):

	# Since we want zero slowtime to be along the upper edge, we need to reverse the input array.
	y_axis_set = np.flip(y_axis_set, 0)


	y_axis_min = 0
	y_axis_max = y_axis_set.shape[0] * time_per_frame

	fig, ax = plt.subplots()
	ax.imshow(y_axis_set,
			aspect = 'auto',
			extent = (x_axis[0], x_axis[-1], y_axis_max, y_axis_min),
		)


	ax.set(xlabel='Time (ns)', ylabel='Time Ago (s)', title='Time vs Slow-Time')


def plot_sweeps(frequencies, sweeps_set, time_per_frame):

	# Messily unpack the sweep data structure.
	# There are a unch of assumptions here, mostly based around the fact that
	# we're only ever acquiring one path.
	complex_sweeps = [
			tmp[0][1]['data']
		for
			tmp
		in
			sweeps_set
	]


	fft_data = [
			phase_correct_ifft(
				data         = tmp,
				start_f      = frequencies[0],
				stop_f       = frequencies[-1],
				npts         = len(frequencies),
				cable_delays = CABLE_DELAYS
			)
		for
			tmp
		in
			complex_sweeps
	]

	# Since we're not changing the sweep parameters, the time axis for the
	# FFT data is constant across the entire dataset. Therefore, we can just pick
	# any time-axis set, and use that everywhere.
	fft_time_axis = fft_data[0][1]

	fft_mag = [log_mag(tmp[0]) for tmp in fft_data]

	sweeps_mag = [log_mag(tmp) for tmp in complex_sweeps]

	fft_mag = np.vstack(fft_mag)
	sweeps_mag = np.vstack(sweeps_mag)

	fig, ax = plt.subplots()
	for idx, sweep_array in enumerate(sweeps_mag[:10,...]):
		ax.plot(frequencies, sweep_array, label='Sweep %s' % idx)


	ax.set(xlabel='Frequency (MHz)', ylabel='Magnitude (dB)', title='Frequency vs Magnitude')
	plt.legend()


	fig, ax = plt.subplots()
	for idx, fft_magnitude in enumerate(fft_mag[:10]):
		ax.plot(fft_time_axis, fft_magnitude, label='FFT Sweep %s' % idx)


	ax.set(xlabel='Time (ns)', ylabel='Magnitude (dB)', title='Time vs Magnitude')
	plt.legend()


	waterfall_plot(fft_mag, fft_time_axis, time_per_frame)

	plt.show()




def get_sweeps(count):
	'''
	Acquire `count` frames from the AVMU, and return them (as well as some
	frequency/time frame metadata)
	'''

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

	device.start()


	assert device.getPreciseTimePerFrame() > 0

	state = device.getState()
	print("AVMU State", state)

	sweeps = []

	device.beginAsync()
	start_time = time.time()

	for _ in range(count):

		device.measure()
		sweep_data = device.extractAllPaths()
		sweeps.append(sweep_data)
		print("Acquired sweep (%s)" % (len(sweeps), ))

	stop_time = time.time()
	device.haltAsync()

	time_per_frame = device.getPreciseTimePerFrame()

	device.stop()

	print("Acquired %s sweeps! Time per sweep: %s. Total time: %s (calculated: %s)" % (
			len(sweeps),
			time_per_frame,
			stop_time - start_time,
			len(sweeps) * time_per_frame
		)
	)

	return frequencies, sweeps, time_per_frame


def run():
	print("Running minimal demo!")

	frequencies, sweeps, time_per_frame = get_sweeps(SWEEP_COUNT)
	plot_sweeps(frequencies, sweeps, time_per_frame)


if __name__ == '__main__':
	import logging
	logging.basicConfig(level=logging.INFO)

	run()
