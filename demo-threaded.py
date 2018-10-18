
import time
import queue
import threading
import traceback
import logging

import numpy as np

import avmu

class ThreadExit(Exception):
	pass

def log_mag(inarr):
	return 20 * np.log10(np.absolute(inarr))


class AvmuThread():
	def __init__(self):

		self.command_queue  = queue.Queue()
		self.response_queue = queue.Queue()
		self.avmu_connected = False
		self.log = logging.getLogger("Main.Avmu")

		self.worker_thread      = False
		self.thread_should_exit = False

		self.runstate       = False
		self.avmu           = None
		self.log.info("Avmu Thread running")

		self.hop   = "HOP_45K"

		self.active_paths = []

		self.start_f = 1000
		self.stop_f  = 2000
		self.npts_s  = 1024

		self.serial_buf_sz = 0

		# Paths we're acquiring.
		self.path_vals  = [
				("AVMU_TX_PATH_0", "AVMU_RX_PATH_1"),
				]

		# Map to convert nice readable paths into hardware paths.
		self.paths_map = {
				'P1:P2' : ("AVMU_TX_PATH_0", "AVMU_RX_PATH_1"),
				}

		self.valid_paths = set([
				'P1:P2',
			])

		self.averaging_interval = 4
		self.averages = {}



	def update_acq_params(self, restart=True):
		if not self.avmu:
			return
		state = self.avmu.getState()
		self.log.info("Updating acq params! Current state: %s", state)

		if state == 'TASK_STARTED':
			self.avmu.stop()
		elif state == 'TASK_UNINITIALIZED' or state == 'TASK_STOPPED':
			self.log.info("Restarting task!")
			self.log.info("Current State: %s", state)
		else:
			raise ValueError("Unknown state?")

		state = self.avmu.getState()
		self.log.info("Current state: %s", state)

		self.log.info("Changing acquisition parameters")

		self.avmu.setHopRate(self.hop)
		self.avmu.utilGenerateLinearSweep(startF_mhz=self.start_f, stopF_mhz=self.stop_f, points=self.npts_s)

		self.avmu.clearMeasuredPaths()
		for txp, rxp in self.path_vals:
			self.avmu.addPathToMeasure(txp, rxp)

		if restart:
			self.avmu.start()

		# Clear the running average buffer, because the array size may have changed.
		self.averages = {}

	####################################################################################################################################
	####################################################################################################################################
	####################################################################################################################################

	def handle_run_command(self, params):
		newstate = params[0]

		if not self.avmu and newstate is True:
			self.log.error("You have to connect to a AVMU first!")
			return

		if self.runstate == newstate and newstate is True:
			self.log.error("Run command that matches current state?")

		else:
			if newstate is True:

				self.log.info("Starting avmu task")
				self.update_acq_params(restart=False)
				self.avmu.start()
				self.runstate = True

			else:
				if self.avmu != None and self.runstate:
					self.log.info("Stopping avmu task")
					self.avmu.stop()
					self.runstate = False
				else:
					self.log.warning("Non True runstate when not running?")

	def handle_sweep_command(self, params):
		self.log.info("Updating sweep settings")
		self.npts_s , self.start_f, self.stop_f, self.hop = params
		self.update_acq_params()


	def handle_connect_command(self, params):
		if not self.avmu_connected:
			try:
				self.log.info("Connecting to AVMU with params: %s", params)
				self.avmu = avmu.AvmuInterface()

				ip_addr, ip_port = params

				self.avmu.setIPAddress(ip_addr)
				self.avmu.setIPPort(ip_port)
				self.avmu.setTimeout(500)

				self.avmu.initialize()

				self.avmu.setHopRate(self.hop)

				self.avmu.utilGenerateLinearSweep(startF_mhz=self.start_f, stopF_mhz=self.stop_f, points=self.npts_s)


			except avmu.Avmu_Exception as dummy_e:
				self.log.error("Failure connecting to the hardware!")
				for line in traceback.format_exc().split("\n"):
					self.log.error("	%s", line)
				self.log.error("Please try again, or power-cycle the AVMU.")
				return

			self.avmu_connected = True
		else:
			try:
				self.avmu.stop()
			except avmu.Avmu_Exception:
				pass

			self.avmu = None
			self.log.info("avmu Disconnected")
			self.avmu_connected = False
			self.runstate      = False


	def handle_path_command(self, params):

		self.path_vals    = []
		self.active_paths = []

		for pathval in params:
			if not pathval in self.valid_paths:
				self.log.error("The sample path MUST be one of the set: '%s'. Received: '%s'", self.valid_paths, params)
				return

			self.active_paths.append(pathval)
			pathval = pathval.split()[0]
			if self.paths_map[pathval] not in self.path_vals:
				self.path_vals.append(self.paths_map[pathval])

		assert len(self.path_vals) == len(set(self.path_vals))
		self.update_acq_params()

		self.log.info("Actively measured paths: %s", self.active_paths)



	####################################################################################################################################
	####################################################################################################################################
	####################################################################################################################################

	def dispatch(self, command):
		assert isinstance(command, tuple), "All commands must be a (command, params) tuple!"
		assert len(command) == 2, "All commands must be a (command, params) tuple!"

		command, params = command
		self.log.info("Command message: '%s' - '%s'", command, params)
		if command == "connect":
			self.handle_connect_command(params)
		elif command == "path":
			self.handle_path_command(params)
		elif command == "sweep":
			self.handle_sweep_command(params)
		elif command == "run":
			self.handle_run_command(params)
		elif command == "stop":
			self.runstate = False
		elif command == "halt" and params is True:
			raise ThreadExit("Exiting avmu process!")

		else:
			self.log.error("Unknown command: '%s'", command)
			self.log.error("Command parameters: '%s'", params)


	def get_fft(self, data):

		data_len = data.shape[0]

		# Apply windowing (needs to be an elementwise multiplication)
		data = np.multiply(data, np.hanning(data_len))

		# Pad the start of the array for phase-correctness, and
		# the end to make the calculation a power of N
		step_val = abs(self.start_f - self.stop_f) / self.npts_s
		start_padding = max(int(self.start_f/step_val), 0)

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

		fft_data = np.fft.ifft(arr)

		# Chop off the negative time component (we don't care about it here)
		# Someone doing fancier stuff could put it back.
		fft_data = fft_data[:output_size//2]
		fft_data = np.absolute(fft_data)

		if self.start_f == self.stop_f:
			return fft_data, np.array(range(fft_data.shape[0]))

		pts = np.array(range(fft_data.shape[0]))

		# Convert to hertz
		step_val = step_val * 1e6
		pts = pts * (1 / (len(pts) * step_val * 2))

		pts = pts * 1e9
		return fft_data, pts

	def get_data(self):

		try:
			self.avmu.measure()
		except avmu.Avmu_Exception_No_Response:
			self.log.info("Avmu Exception No Response. Attempting to restart acquisition.")
			self.avmu.stop()
			# Be double plus sure we're stopped.
			try:
				self.avmu.stop()
			except avmu.Avmu_Exception_Wrong_State:
				pass
			self.log.info("Avmu Acquisition halted. Restarting...")
			time.sleep(0.1)

			self.avmu.setHopRate(self.hop)
			self.avmu.utilGenerateLinearSweep(startF_mhz=self.start_f, stopF_mhz=self.stop_f, points=self.npts_s)

			time.sleep(0.1)
			self.avmu.start()
			return
		except avmu.Avmu_Exception_No_Measured_Paths:
			# No paths selected to measure. Just do nothing.
			time.sleep(0.1)
			return

		compensated_data = {}

		fft_data = {}
		fft_pts  = []

		frequencies = self.avmu.getFrequencies()

		sweep_data = self.avmu.extractAllPaths()

		for tx_info, sweep in sweep_data:

			path_data = sweep['data']
			path = (tx_info['tx_path'], tx_info['rx_path'])

			fft_data[path], fft_pts = self.get_fft(path_data)
			compensated_data[path] = log_mag(path_data)

		response = {
			'comp_data' : compensated_data,
			'pts'       : frequencies,
			'fft_data'  : fft_data,
			'fft_pts'   : fft_pts,
		}

		# Sweep data is ready, here
		self.response_queue.put(("sweep", response))


	def process_rx_data(self):

		if self.runstate and self.avmu:
			self.get_data()

	def process_commands(self):

		try:
			while True:
				new_cmd = self.command_queue.get_nowait()
				self.dispatch(new_cmd)
		except queue.Empty:
			return


	def worker_thread_loop(self):
		while not self.thread_should_exit:
			self.process_commands()
			self.process_rx_data()
			time.sleep(0.01)

		self.log.info("Worker thread has exited")
		self.shutdown()

	def start_thread(self):
		self.worker_thread = threading.Thread(target=self.worker_thread_loop)
		self.worker_thread.start()

	def stop_thread(self):
		# Signal the worker to exit.
		self.thread_should_exit = True
		# And join on it.
		self.worker_thread.join()

	def shutdown(self):
		if self.avmu:
			print("Stopping current task (if any)")
			try:
				self.avmu.stop()
			except avmu.Avmu_Exception:
				pass
			print("Freeing current task")
			del self.avmu

			print("Task freed")

	def send_worker_command(self, command, params):
		self.command_queue.put((command, params))


	def get_from_worker_queue(self):
		'''
		Thread-safe data retreival call.
		If you've launched the runner in a thread,
		this can be called from another thread to extract
		the acquired data.
		'''

		try:
			return self.response_queue.get_nowait()
		except queue.Empty:
			return None

def go():
	# Debug logging.
	logging.basicConfig(level=logging.INFO)

	avmut = AvmuThread()
	avmut.start_thread()

	avmut.send_worker_command("connect", ("192.168.1.219", 1027))

	# Sweep commands are num points, start f, stop f, hop rate
	avmut.send_worker_command("sweep", (1024, 1000, 2000, "HOP_45K"))
	avmut.send_worker_command("run", (True, ))

	data = []

	for x in range(20):
		time.sleep(1)

		new_dat = avmut.get_from_worker_queue()
		while new_dat:
			data.append(new_dat)
			new_dat = avmut.get_from_worker_queue()

		print("Loop %s, data size: %s" % (x, len(data)))

	print("Stopping acquisition")
	avmut.send_worker_command("run", (False, ))
	print("Shutting down AVMU Interface")
	avmut.stop_thread()
	print("Done!")

	print("Acquired %s sweeps" % len(data))



if __name__ == "__main__":
	go()
