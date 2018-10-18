'''
# #########################################################################

Python api to AKELA Inc's AVMU hardware.

Note: This library is a relatively thin wrapper on top of
the C/C++ AVMU DLL interface. In general, the documentation
for the C interface is more complete, and generally more likely
to be kept completely up to date. Please check that documentation
in case of ambiguities, before contacting support.

Author: Connor Wolf <cwolf@akelainc.com>

# #########################################################################
'''

import logging
import numpy as np
from . import dll_loader
from . import avmu_exceptions

class AvmuInterface(object):



	def __init__(self, share_from_interface = None):
		'''
		Create the base AVMU interface class.

		For multi-AVMU operation, pass the first created interface
		to any additional interface class instances. This allows all
		the interface instances to share the same underlying communication
		objects, which is needed for synchronized operation.

		Note: If you don't share the communcation object, calls
		such as broadcastBeginCommand() will not operate properly.

		Unfortunately, there is no coherent way to validate this
		in the library code, so it's left up to the user.

		Note: All library functions can theoretically raise  :class:`~avmu.avmu_exceptions.Avmu_Exception_Bad_Handle`
		if the internal task handle has been corrupted. As such, this particular exception will not be explicitly
		enumerated for every possible call.

		'''


		self.log = logging.getLogger("Main.Dll")

		self.log.debug("Loading DLL")

		self.ffi, self.dll = dll_loader.load_ffi_interface()

		self.log.debug("Constructing constant mapping tables.")
		self.___construct_map_tables()

		self.task_handle = self.__createTask(share_from_interface)

		self.measured_paths = []

		self.serial_buf_sz = 0
		self.active_receivers = [0]

	def __del__(self):
		try:
			self.__deleteTask(self.task_handle)
		except AttributeError:
			print("WARNING: Error when trying to delete task handle!")

	def __repr__(self):
		ret = "<AvmuInterface for radar {}:{} state {}, handle {}>".format(
			self.getIPAddress(),
			self.getIPPort(),
			self.getState(),

			# This is legit kind of horrible.
			# Only thing that makes it even marginally not-bad is that
			# it's only for printing an error message.
			str(self.task_handle).strip(">").split(" ")[-1]
			)

		return ret


	def __getRawTaskHandle(self):
		self.log.debug("__getRawTaskHandle call")
		return self.task_handle

	def __createTask(self, fromtask):
		self.log.debug("__createTask call")
		# Signature: TaskHandle createTask();
		self.log.debug("Creating task.")
		if fromtask:
			th = self.dll.createSharedTask(fromtask.__getRawTaskHandle())
		else:
			th = self.dll.createTask()

		return th

	def __deleteTask(self, task_handle):
		self.log.debug("__deleteTask call")
		# Signature: void deleteTask(TaskHandle t);
		self.log.info("Destroying task.")
		self.dll.deleteTask(task_handle)


	def ___construct_map_tables(self):




		self.log.debug("___construct_map_tables call")
		self.errors = {
			self.dll.ERR_OK                                 : None,
			self.dll.ERR_BAD_ATTEN                          : avmu_exceptions.Avmu_Exception_Bad_Atten,
			self.dll.ERR_BAD_CAL                            : avmu_exceptions.Avmu_Exception_Bad_Cal,
			self.dll.ERR_BAD_HANDLE                         : avmu_exceptions.Avmu_Exception_Bad_Handle,
			self.dll.ERR_BAD_HOP                            : avmu_exceptions.Avmu_Exception_Bad_Hop,
			self.dll.ERR_BAD_PATH                           : avmu_exceptions.Avmu_Exception_Bad_Path,
			self.dll.ERR_BAD_PROM                           : avmu_exceptions.Avmu_Exception_Bad_Prom,
			self.dll.ERR_BYTES                              : avmu_exceptions.Avmu_Exception_Bytes,
			self.dll.ERR_EMPTY_PROM                         : avmu_exceptions.Avmu_Exception_Empty_Prom,
			self.dll.ERR_FEATURE_NOT_PRESENT                : avmu_exceptions.Avmu_Exception_Feature_Not_Present,
			self.dll.ERR_FREQ_OUT_OF_BOUNDS                 : avmu_exceptions.Avmu_Exception_Freq_Out_Of_Bounds,
			self.dll.ERR_INTERRUPTED                        : avmu_exceptions.Avmu_Exception_Interrupted,
			self.dll.ERR_MISSING_ATTEN                      : avmu_exceptions.Avmu_Exception_Missing_Atten,
			self.dll.ERR_MISSING_FREQS                      : avmu_exceptions.Avmu_Exception_Missing_Freqs,
			self.dll.ERR_MISSING_HOP                        : avmu_exceptions.Avmu_Exception_Missing_Hop,
			self.dll.ERR_MISSING_IP                         : avmu_exceptions.Avmu_Exception_Missing_Ip,
			self.dll.ERR_MISSING_PORT                       : avmu_exceptions.Avmu_Exception_Missing_Port,
			self.dll.ERR_NO_ATTEN_PRESENT                   : avmu_exceptions.Avmu_Exception_No_Attenuator_Present,
			self.dll.ERR_NO_PATHS_MEASURED                  : avmu_exceptions.Avmu_Exception_No_Measured_Paths,
			self.dll.ERR_NO_RESPONSE                        : avmu_exceptions.Avmu_Exception_No_Response,
			self.dll.ERR_PATH_ALREADY_MEASURED              : avmu_exceptions.Avmu_Exception_Path_Already_Measured,
			self.dll.ERR_PROG_OVERFLOW                      : avmu_exceptions.Avmu_Exception_Prog_Overflow,
			self.dll.ERR_SOCKET                             : avmu_exceptions.Avmu_Exception_Socket,
			self.dll.ERR_TOO_MANY_POINTS                    : avmu_exceptions.Avmu_Exception_Too_Many_Points,
			self.dll.ERR_UNKNOWN_FEATURE                    : avmu_exceptions.Avmu_Exception_Unknown_Feature,
			self.dll.ERR_WRONG_PROGRAM_TYPE                 : avmu_exceptions.Avmu_Exception_Wrong_Program_Type,
			self.dll.ERR_WRONG_STATE                        : avmu_exceptions.Avmu_Exception_Wrong_State,
			self.dll.ERR_BAD_IP_PORT                        : avmu_exceptions.Avmu_Exception_Bad_IP_Port,
			self.dll.ERR_TASK_ARRAY_INVALID                 : avmu_exceptions.Avmu_Exception_Task_Array_Invalid,
			self.dll.ERR_PATH_HAS_NO_DATA                   : avmu_exceptions.Avmu_Exception_Path_Has_No_Data,
			# self.dll.ERR_INDEX_OUT_OF_BOUNDS                : avmu_exceptions.Avmu_Exception_Err_Index_Out_Of_Bounds,
			# self.dll.ERR_INVALID_PARAMETER                  : avmu_exceptions.Avmu_Exception_Err_Invalid_Parameter,
			# self.dll.ERR_PROM_INVALID_FEATURE_CONFIGURATION : avmu_exceptions.Avmu_Exception_Err_Prom_Invalid_Feature_Configuration,

		}

		self.hops = {
			'HOP_UNDEFINED' : self.dll.HOP_UNDEFINED,
			'HOP_90K'       : self.dll.HOP_90K,
			'HOP_45K'       : self.dll.HOP_45K,
			'HOP_30K'       : self.dll.HOP_30K,
			'HOP_15K'       : self.dll.HOP_15K,
			'HOP_7K'        : self.dll.HOP_7K,
			'HOP_3K'        : self.dll.HOP_3K,
			'HOP_2K'        : self.dll.HOP_2K,
			'HOP_1K'        : self.dll.HOP_1K,
			'HOP_550'       : self.dll.HOP_550,
			'HOP_312'       : self.dll.HOP_312,
			'HOP_156'       : self.dll.HOP_156,
			'HOP_78'        : self.dll.HOP_78,
			'HOP_39'        : self.dll.HOP_39,
			'HOP_20'        : self.dll.HOP_20,
		}


		self.tx_paths = {
			'AVMU_TX_PATH_0'    : self.dll.AVMU_TX_PATH_0,
			'AVMU_TX_PATH_1'    : self.dll.AVMU_TX_PATH_1,
			'AVMU_TX_PATH_2'    : self.dll.AVMU_TX_PATH_2,
			'AVMU_TX_PATH_3'    : self.dll.AVMU_TX_PATH_3,
			'AVMU_TX_PATH_4'    : self.dll.AVMU_TX_PATH_4,
			'AVMU_TX_PATH_5'    : self.dll.AVMU_TX_PATH_5,
			'AVMU_TX_PATH_6'    : self.dll.AVMU_TX_PATH_6,
			'AVMU_TX_PATH_7'    : self.dll.AVMU_TX_PATH_7,
			'AVMU_TX_PATH_NONE' : self.dll.AVMU_TX_PATH_NONE,
		}
		self.rx_paths = {
			'AVMU_RX_PATH_0'    : self.dll.AVMU_RX_PATH_0,
			'AVMU_RX_PATH_1'    : self.dll.AVMU_RX_PATH_1,
			'AVMU_RX_PATH_2'    : self.dll.AVMU_RX_PATH_2,
			'AVMU_RX_PATH_3'    : self.dll.AVMU_RX_PATH_3,
			'AVMU_RX_PATH_4'    : self.dll.AVMU_RX_PATH_4,
			'AVMU_RX_PATH_5'    : self.dll.AVMU_RX_PATH_5,
			'AVMU_RX_PATH_6'    : self.dll.AVMU_RX_PATH_6,
			'AVMU_RX_PATH_7'    : self.dll.AVMU_RX_PATH_7,
			'AVMU_RX_PATH_NONE' : self.dll.AVMU_RX_PATH_NONE,
		}


		self.tx_paths_int = {
			'AVMU_TX_PATH_0'    : 0,
			'AVMU_TX_PATH_1'    : 1,
			'AVMU_TX_PATH_2'    : 2,
			'AVMU_TX_PATH_3'    : 3,
			'AVMU_TX_PATH_4'    : 4,
			'AVMU_TX_PATH_5'    : 5,
			'AVMU_TX_PATH_6'    : 6,
			'AVMU_TX_PATH_7'    : 7,
			'AVMU_TX_PATH_NONE' : -1,
		}
		self.rx_paths_int = {
			'AVMU_RX_PATH_0'    :  0,
			'AVMU_RX_PATH_1'    :  1,
			'AVMU_RX_PATH_2'    :  2,
			'AVMU_RX_PATH_3'    :  3,
			'AVMU_RX_PATH_4'    :  4,
			'AVMU_RX_PATH_5'    :  5,
			'AVMU_RX_PATH_6'    :  6,
			'AVMU_RX_PATH_7'    :  7,
			'AVMU_RX_PATH_NONE' : -1,
		}

		self.tx_paths_int_enum = {
			 0 : self.dll.AVMU_TX_PATH_0,
			 1 : self.dll.AVMU_TX_PATH_1,
			 2 : self.dll.AVMU_TX_PATH_2,
			 3 : self.dll.AVMU_TX_PATH_3,
			 4 : self.dll.AVMU_TX_PATH_4,
			 5 : self.dll.AVMU_TX_PATH_5,
			 6 : self.dll.AVMU_TX_PATH_6,
			 7 : self.dll.AVMU_TX_PATH_7,
			-1 : self.dll.AVMU_TX_PATH_NONE,
		}

		self.rx_paths_int_enum = {
			 0 : self.dll.AVMU_RX_PATH_0,
			 1 : self.dll.AVMU_RX_PATH_1,
			 2 : self.dll.AVMU_RX_PATH_2,
			 3 : self.dll.AVMU_RX_PATH_3,
			 4 : self.dll.AVMU_RX_PATH_4,
			 5 : self.dll.AVMU_RX_PATH_5,
			 6 : self.dll.AVMU_RX_PATH_6,
			 7 : self.dll.AVMU_RX_PATH_7,
			-1 : self.dll.AVMU_RX_PATH_NONE,
		}

		self.tx_paths_enum_int = {
			self.dll.AVMU_TX_PATH_0    :  0,
			self.dll.AVMU_TX_PATH_1    :  1,
			self.dll.AVMU_TX_PATH_2    :  2,
			self.dll.AVMU_TX_PATH_3    :  3,
			self.dll.AVMU_TX_PATH_4    :  4,
			self.dll.AVMU_TX_PATH_5    :  5,
			self.dll.AVMU_TX_PATH_6    :  6,
			self.dll.AVMU_TX_PATH_7    :  7,
			self.dll.AVMU_TX_PATH_NONE : -1,

		}

		self.rx_paths_enum_int = {
			self.dll.AVMU_RX_PATH_0    :  0,
			self.dll.AVMU_RX_PATH_1    :  1,
			self.dll.AVMU_RX_PATH_2    :  2,
			self.dll.AVMU_RX_PATH_3    :  3,
			self.dll.AVMU_RX_PATH_4    :  4,
			self.dll.AVMU_RX_PATH_5    :  5,
			self.dll.AVMU_RX_PATH_6    :  6,
			self.dll.AVMU_RX_PATH_7    :  7,
			self.dll.AVMU_RX_PATH_NONE : -1,
		}

		self.tx_paths_enum_str = {
			self.dll.AVMU_TX_PATH_0    : 'AVMU_TX_PATH_0',
			self.dll.AVMU_TX_PATH_1    : 'AVMU_TX_PATH_1',
			self.dll.AVMU_TX_PATH_2    : 'AVMU_TX_PATH_2',
			self.dll.AVMU_TX_PATH_3    : 'AVMU_TX_PATH_3',
			self.dll.AVMU_TX_PATH_4    : 'AVMU_TX_PATH_4',
			self.dll.AVMU_TX_PATH_5    : 'AVMU_TX_PATH_5',
			self.dll.AVMU_TX_PATH_6    : 'AVMU_TX_PATH_6',
			self.dll.AVMU_TX_PATH_7    : 'AVMU_TX_PATH_7',
			self.dll.AVMU_TX_PATH_NONE : 'AVMU_TX_PATH_NONE',

		}

		self.rx_paths_enum_str = {
			self.dll.AVMU_RX_PATH_0    : 'AVMU_RX_PATH_0',
			self.dll.AVMU_RX_PATH_1    : 'AVMU_RX_PATH_1',
			self.dll.AVMU_RX_PATH_2    : 'AVMU_RX_PATH_2',
			self.dll.AVMU_RX_PATH_3    : 'AVMU_RX_PATH_3',
			self.dll.AVMU_RX_PATH_4    : 'AVMU_RX_PATH_4',
			self.dll.AVMU_RX_PATH_5    : 'AVMU_RX_PATH_5',
			self.dll.AVMU_RX_PATH_6    : 'AVMU_RX_PATH_6',
			self.dll.AVMU_RX_PATH_7    : 'AVMU_RX_PATH_7',
			self.dll.AVMU_RX_PATH_NONE : 'AVMU_RX_PATH_NONE',
		}


		self.prog_type = {
			'PROG_ASYNC'          : self.dll.PROG_ASYNC,
			'PROG_SYNC'           : self.dll.PROG_SYNC,

		}
		self.run_state = {
			'TASK_RUNNING'        : self.dll.TASK_RUNNING,
			'TASK_STARTED'        : self.dll.TASK_STARTED,
			'TASK_STOPPED'        : self.dll.TASK_STOPPED,
			'TASK_UNINITIALIZED'  : self.dll.TASK_UNINITIALIZED,
		}
		self.sync_pulse_mode = {
			'SYNC_IGNORE'         : self.dll.SYNC_IGNORE,
			'SYNC_GENERATE'       : self.dll.SYNC_GENERATE,
			'SYNC_RECEIVE'        : self.dll.SYNC_RECEIVE,
		}

		self.if_gain_settings = {
				'AVMU_GAIN_USE_DEFAULT' : self.dll.AVMU_GAIN_USE_DEFAULT,
				'AVMU_GAIN_0'           : self.dll.AVMU_GAIN_0,
				'AVMU_GAIN_3'           : self.dll.AVMU_GAIN_3,
				'AVMU_GAIN_6'           : self.dll.AVMU_GAIN_6,
				'AVMU_GAIN_9'           : self.dll.AVMU_GAIN_9,
				'AVMU_GAIN_12'          : self.dll.AVMU_GAIN_12,
				'AVMU_GAIN_15'          : self.dll.AVMU_GAIN_15,
				'AVMU_GAIN_18'          : self.dll.AVMU_GAIN_18,
				'AVMU_GAIN_21'          : self.dll.AVMU_GAIN_21,
				'AVMU_GAIN_24'          : self.dll.AVMU_GAIN_24,
				'AVMU_GAIN_27'          : self.dll.AVMU_GAIN_27,
				'AVMU_GAIN_30'          : self.dll.AVMU_GAIN_30,
				'AVMU_GAIN_33'          : self.dll.AVMU_GAIN_33,
				'AVMU_GAIN_36'          : self.dll.AVMU_GAIN_36,
				'AVMU_GAIN_39'          : self.dll.AVMU_GAIN_39,
				'AVMU_GAIN_42'          : self.dll.AVMU_GAIN_42,
				'AVMU_GAIN_45'          : self.dll.AVMU_GAIN_45,
		}

		self.if_gain_inverse = {
				self.dll.AVMU_GAIN_USE_DEFAULT : 'AVMU_GAIN_USE_DEFAULT',
				self.dll.AVMU_GAIN_0           : 'AVMU_GAIN_0',
				self.dll.AVMU_GAIN_3           : 'AVMU_GAIN_3',
				self.dll.AVMU_GAIN_6           : 'AVMU_GAIN_6',
				self.dll.AVMU_GAIN_9           : 'AVMU_GAIN_9',
				self.dll.AVMU_GAIN_12          : 'AVMU_GAIN_12',
				self.dll.AVMU_GAIN_15          : 'AVMU_GAIN_15',
				self.dll.AVMU_GAIN_18          : 'AVMU_GAIN_18',
				self.dll.AVMU_GAIN_21          : 'AVMU_GAIN_21',
				self.dll.AVMU_GAIN_24          : 'AVMU_GAIN_24',
				self.dll.AVMU_GAIN_27          : 'AVMU_GAIN_27',
				self.dll.AVMU_GAIN_30          : 'AVMU_GAIN_30',
				self.dll.AVMU_GAIN_33          : 'AVMU_GAIN_33',
				self.dll.AVMU_GAIN_36          : 'AVMU_GAIN_36',
				self.dll.AVMU_GAIN_39          : 'AVMU_GAIN_39',
				self.dll.AVMU_GAIN_42          : 'AVMU_GAIN_42',
				self.dll.AVMU_GAIN_45          : 'AVMU_GAIN_45',
		}


	def __check_ret(self, ret_val):
		self.log.debug("__check_ret call")
		try:
			state = self.getState()
		except Exception:
			self.log.error("Failed to query current state!")
			state = "Unknown!"

		assert ret_val in self.errors, "Unknown returned error code: %s. Current state: %s" % (ret_val, state)
		err = self.errors[ret_val]
		if err:
			raise err("Call returned error value: %s. Current state: %s" % (ret_val, state))


	#################################################################################
	#        Configuration
	#################################################################################

	def addPathToMeasure(self, tx_path, rx_path, who_is_transmitting=None, port_is_transmitting=None):
		'''
		Add a path to measure.

		Adds a path to the list of active paths that will be
		measured when data is actually acquired.

		Args:
			tx_path (str): Transmitting port of the path to add. Note that
			                 this can very well be TX_NONE, if your application is
			                 using multiple AVMUs, and one of the other AVMUs is
			                 the one actively transmitting.
			rx_path (str): RX Path for the combo. This can be RX_NONE if there
			                is no need for the associated rx data. Note that RX_NONE
			                will still return data (as the transmitter will still
			                need to do the associated frequency stepping), but the
			                return content will be only cross-board leakage within
			                the AVMU.

		Returns:
			Nothing

		raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Bad_Path`:   if a path value specified is invalid.

		'''
		self.log.debug("addPathToMeasure call")
		# Signature: ErrCode addPathToMeasure(TaskHandle t, RFPath path);
		if not tx_path in self.tx_paths: raise avmu_exceptions.Avmu_Exception_Bad_Path("Invalid TX Path: '%s'" % (tx_path, ))
		if not rx_path in self.rx_paths: raise avmu_exceptions.Avmu_Exception_Bad_Path("Invalid RX Path: '%s'" % (rx_path, ))

		items = [
			("tx_path",              tx_path, str),
			("rx_path",              rx_path, str),
			("who_is_transmitting",  who_is_transmitting, (int, type(None))),
			("port_is_transmitting", port_is_transmitting, (int, type(None)))
		]

		for name, value, expected_type in items:
			assert isinstance(value, expected_type), "Parameter %s is not of expected type (%s). Passed type %s, value %s" % (
				name, expected_type, type(value), value)

		self.log.debug("Adding path to measure: %s -> %s (transmiting:  %s -> %s)", tx_path, rx_path, who_is_transmitting, port_is_transmitting)
		self.measured_paths.append((who_is_transmitting, port_is_transmitting, self.tx_paths_int[tx_path], self.rx_paths_int[rx_path]))
		ret = self.dll.addPathToMeasure(self.task_handle, self.tx_paths[tx_path], self.rx_paths[rx_path])
		self.__check_ret(ret)

	def clearMeasuredPaths(self):
		'''
		Clear list of paths being measured.

		Returns:
			Nothing

		'''
		self.log.debug("clearMeasuredPaths call")
		# Signature: ErrCode clearMeasuredPaths(TaskHandle t);
		self.log.debug("Clearing measured paths")
		self.measured_paths = []
		ret = self.dll.clearMeasuredPaths(self.task_handle)
		self.__check_ret(ret)

	###############################################################

	def getFrequencies(self):
		'''

		Get a list containing the actual frequencies the hardware will sample for
		the configured sweep in task `t`. Units are MHz.

		The actual frequency points can differ from the requested frequency points
		because the hardware has fixed precision, and cannot achieve every arbitrary
		frequency value within its tunable bands. The values in this list are the
		requested frequency points after snapping them to the closest achievable
		frequency.

		Returns:
			list of floating point frequencies, in MHz


		'''
		self.log.debug("getFrequencies call")
		# Signature: ErrCode getFrequencies(TaskHandle t, double* freqs, int pts_in_freqs);
		npts = self.getNumberOfFrequencies()
		freq_arr = self.ffi.new("double[] ", [0] * npts)
		ret = self.dll.getFrequencies(self.task_handle, freq_arr, npts)
		self.__check_ret(ret)
		return list(freq_arr)

	def setFrequencies(self, freqs):
		'''
		Set the frequencies to measure during each sweep. Units are MHz.

		Note that the AVMU frequency generation
		hardware has fixed precision and so the generated frequency may not be exactly
		equal to the requested frequency. This function silently converts all requested
		frequencies to frequencies that can be exactly generated by the hardware.
		This has important implications for Doppler noise when doing a linear sweep.
		AKELA recommends using the function :func:`utilFixLinearSweepLimits()` to ensure
		every frequency is exactly generateable and that the frequencies are equally
		spaced. Use the :func:`getFrequencies()` function to get the actual frequencies being
		generated.

		Args:
			freqs (list): array of frequencies to sample, in MHz

		Returns:
			Nothing

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STOPPED state
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Too_Many_Points` if N is larger than \
			                                the maximum allowed (see HardwareDetails)
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Freq_Out_Of_Bounds` if a frequency is \
			                                beyond the allowed min/max. (You can get the min and max from \
			                                the HardwareDetails struct returned by :func:`getHardwareDetails()`)
		'''
		self.log.debug("setFrequencies call")
		# Signature: ErrCode setFrequencies(TaskHandle t, const double* freqs, const unsigned int N);
		freq_arr = self.ffi.new("double[] ", freqs)
		ret = self.dll.setFrequencies(self.task_handle, freq_arr, len(freqs))
		self.__check_ret(ret)

	###############################################################

	def getHopRate(self):
		'''
		Get the frequency hopping rate associated with this Task object.
		If no rate has yet been set, this function returns ``HOP_UNDEFINED``.

		Returns:
			Current hop rate as a string.
		'''

		self.log.debug("getHopRate call")
		# Signature: HopRate getHopRate(TaskHandle t);
		ret = self.dll.getHopRate(self.task_handle)
		for key, value in self.hops.items():
			if value == ret:
				self.log.debug("Current hop rate: %s", key)
				return key
		raise avmu_exceptions.Avmu_Exception_Missing_Hop("getHopRate() returned an unknown hop-rate value: %s" % ret)

	def setHopRate(self, hop_str):
		'''
		Set the frequency hopping rate. See the values defined in the "HopRate" type above.

		Args:
			hop_str (str): The new hop rate.

		Returns:
			Nothing

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Bad_Hop` if there was something wrong with the hop rate parameter
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the ``TASK_UNINITIALIZED`` or ``TASK_STOPPED`` state
		'''

		self.log.debug("setHopRate call")
		# Signature: ErrCode setHopRate(TaskHandle t, const HopRate rate);
		self.log.debug("Setting hop rate to: %s", hop_str)
		assert hop_str != "HOP_UNDEFINED", "You cannot set the hop rate to undefined!"
		assert hop_str in self.hops, "Invalid hop rate: '%s'!" % hop_str
		ret = self.dll.setHopRate(self.task_handle, self.hops[hop_str])
		self.__check_ret(ret)

	###############################################################

	def getIPAddress(self):
		'''
		Get the current AVMU IP address for the Task object.
		When no IP has yet been set, this will return a NULL
		char*.

		Returns:
			string of the current remote IP. If the IP is unset, returns ``None``
		'''

		self.log.debug("getIPAddress call")
		# Signature: const char* getIPAddress(TaskHandle t);
		ret = self.dll.getIPAddress(self.task_handle)

		if ret == self.ffi.NULL:
			self.log.debug("Null remote IP!")
			return None
		ret = self.ffi.string(ret).decode("ascii")
		self.log.debug("Current remote IP address: %s", ret)
		return ret

	def setIPAddress(self, ip_address):
		'''

		Sets the IPv4 address of the unit to communicate with.  \
		The ipv4 parameter is copied into the Task's memory.  \
		On success the Task's state will be ``TASK_UNINITIALIZED``. \

		Args:
			ip_address (str) IP representation, e.g. "192.168.1.207", etc...

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State`if the Task is not in the ``TASK_UNINITIALIZED`` or ``TASK_STOPPED`` state

		'''
		self.log.debug("setIPAddress call")
		# Signature: ErrCode setIPAddress(TaskHandle t, const char* ipv4);
		assert ip_address.strip("0123456789.") == "", "Invalid characters in IP: '%s' (full string: '%s')" % (ip_address.strip("0123456789."), ip_address)
		self.log.debug("Setting remote IP address to: %s", ip_address)
		ret = self.dll.setIPAddress(self.task_handle, ip_address.encode("ascii"))
		self.__check_ret(ret)

	###############################################################

	def getIPPort(self):
		'''
		Get the current port for IP communications. When uninitialized, this will default to 0.
		'''
		self.log.debug("getIPPort call")
		# Signature: int getIPPort(TaskHandle t);
		port = self.dll.getIPPort(self.task_handle)
		self.log.debug("Current remote IP port: %s", port)
		return port

	def setIPPort(self, port):
		'''
		 Sets the port on which to communicate with the unit.

		The value of `port` MUST be > 1024, as 1024 is reserved
		for broadcast operations.

		Note that for multi-unit configurations, each unit must be
		assigned a unique port > 1024 (the AVMU units listen on all
		ports, but only respond to broadcast commands on port 1024).
		On success, the Task's state will be ``TASK_UNINITIALIZED``.

		Args:
			port (int) port number

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State`if the Task is not in the ``TASK_UNINITIALIZED`` or ``TASK_STOPPED`` state
		'''

		self.log.debug("setIPPort call")
		# Signature: ErrCode setIPPort(TaskHandle t, const int port);
		self.log.debug("Setting remote IP port to: %s", port)
		ret = self.dll.setIPPort(self.task_handle, port)
		self.__check_ret(ret)

	###############################################################

	def getMeasurementType(self):
		'''
		Get the current measurement ProgramType type.

		Returns:
			(str) Current measurement type.
		'''
		self.log.debug("getMeasurementType call")
		# Signature: ProgramType getMeasurementType(TaskHandle t);
		prog = self.dll.getMeasurementType(self.task_handle)

		for prog_name, prog_val in self.prog_type.items():
			if prog_val == prog:
				return prog_name

		raise avmu_exceptions.Avmu_Exception_Wrong_Program_Type("Unknown program type value (%s)!" % prog)

	def setMeasurementType(self, measure_type):
		'''
		Set the measurement type (synchronous or asynchronous). Note that the AVMU
		defaults to synchonous (PROG_SYNC).

		Args:
			measure_type (str) One of the ProgramType types (``PROG_ASYNC`` or ``PROG_SYNC``).
		'''
		self.log.debug("setMeasurementType call")
		# Signature: ErrCode setMeasurementType(TaskHandle t, const ProgramType type);
		assert measure_type in self.prog_type, "Invalid measurement type!"
		measurement_type_code = self.prog_type[measure_type]
		ret = self.dll.setMeasurementType(self.task_handle, measurement_type_code)
		self.__check_ret(ret)

	###############################################################

	# TODO: Also UNTESTED!
	def setGainSetting(self, gain_setting):
		'''
		Control IF gain.

		The AVMU has the facility for configurable  gain within the IF stage
		of the RF pipeline.

		Args:
			gain_setting (str) A value in the IfGain Enum (e.g. "AVMU_GAIN_*")

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the task is either UNINITIALIZED or STOPPED.

		'''
		self.log.debug("setGainSetting call")
		# ErrCode getIfGain(TaskHandle t, IfGain* new_gain);
		assert gain_setting in self.if_gain_settings, "Invalid gain value!"
		new_if_gain_enum = self.if_gain_settings[gain_setting]
		print("Specified gain: %s, %s" % (gain_setting, new_if_gain_enum))
		ret = self.dll.setIfGain(self.task_handle, new_if_gain_enum)
		self.__check_ret(ret)


	def getGainSetting(self):
		'''
		Get the current IF gain setting.

		Returns:
			(str) Current IF gain settings.
		'''
		self.log.debug("getGainSetting call")
		# ErrCode setIfGain(TaskHandle t, IfGain new_gain);
		current_gain_setting = self.ffi.new("int *", 0)
		ret = self.dll.getIfGain(self.task_handle, current_gain_setting)
		self.__check_ret(ret)

		if current_gain_setting[0] in self.if_gain_inverse:
			return self.if_gain_inverse[current_gain_setting[0]]
		else:
			raise avmu_exceptions.Avmu_Exception("Failed to decode returned gain settings (%s)!" % current_gain_setting[0])


	def setReceiver12dBPad(self, insert_pad):
		'''
		Control whether an optional 12dB pad is inserted in the internal RF chain.


		Args:
			insert_pad (bool): Whether the pad is inserted.
		'''
		self.log.debug("setReceiver12dBPad call")
		# ErrCode getIfGain(TaskHandle t, IfGain* new_gain);
		assert isinstance(insert_pad, bool), "insert_pad must be a boolean!"

		ret = self.dll.setReceiver12dBPad(self.task_handle, insert_pad)
		self.__check_ret(ret)

	def getReceiver12dBPad(self):
		'''
		TODO: Untested!

		Get whether the optional 12DB pad is inserted into the RF chain.

		Returns:
			(bool) True if pad is enabled.
		'''
		self.log.debug("getReceiver12dBPad call")
		# ErrCode setIfGain(TaskHandle t, IfGain new_gain);
		is_inserted = self.ffi.new("bool *", False)
		ret = self.dll.getReceiver12dBPad(self.task_handle, is_inserted)
		self.__check_ret(ret)

		return is_inserted[0]



	###############################################################

	def getNumberOfFrequencies(self):
		'''

		Get the number of frequency points for the sweep configured for
		the Task. If no frequencies have been set, this function returns 0.

		Returns:
			(int) Number of frequency points in the current sweep.

		'''
		self.log.debug("getNumberOfFrequencies call")
		# Signature: unsigned int getNumberOfFrequencies(TaskHandle t);
		freqNum = self.dll.getNumberOfFrequencies(self.task_handle)
		return freqNum


	def utilGenerateLinearSweep(self, startF_mhz, stopF_mhz, points):
		'''

		Generates a linear sweep with the requested parameters. Note that the start and end
		frequency will be adjusted as documented in utilFixLinearSweepLimits() so that all
		frequency points fall on exactly generateable values. This function internally calls
		setFrequencies() with the resulting array. The caller can retrieve the frequency list
		with the getFrequencies() function. Since it changes the frequencies this function
		is only available in the TASK_STOPPED state.

		If `startFreq` == `endFreq`, the hardware will effectively be placed in zero-span
		mode, as it will repeatedly sample the same frequency for the duration of the
		sweep. This is a valid operating mode.

		Args:
			startF_mhz (float) Start frequency of sweep in Mhz
			stopF_mhz (float) End frequency of sweep in Mhz
			N (int) Number of points to sample

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STOPPED state
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Too_Many_Points` if N is larger than \
			                                the maximum allowed (see HardwareDetails)
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Freq_Out_Of_Bounds` if a frequency is \
			                                beyond the allowed min/max. (You can get the min and max from \
			                                the HardwareDetails struct returned by :func:`getHardwareDetails()`)
		'''
		self.log.debug("utilGenerateLinearSweep call")
		# Signature: ErrCode utilGenerateLinearSweep(TaskHandle t, const double startFreq, const double endFreq, const unsigned int N);
		ret = self.dll.utilGenerateLinearSweep(self.task_handle, startF_mhz, stopF_mhz, points)
		self.__check_ret(ret)

	###############################################################

	def getTimeout(self):
		'''
		Get the current UDP socket transport timeout.

		Returns:
			(int) socket timeout, in milliseconds.
		'''
		self.log.debug("getTimeout call")
		# Signature: unsigned int getTimeout(TaskHandle t);
		timeout = self.dll.getTimeout(self.task_handle)
		self.log.debug("Current timeout value: %s ms", timeout)
		return timeout

	def setTimeout(self, timeout_ms):
		'''
		Sets the default time to wait, in milliseconds, for a unit to reply to a command
		before giving up and returning an ERR_NO_RESPONSE condition. For the measurement
		functions, this is the amount of time to wait beyond the expected sweep time.
		When a Task is created, the timeout value defaults to 1000.

		A timeout value of 0 results in non-blocking call, where the call will return
		immediately if there is no data in the OS receive buffer.

		Args:
			timeout_ms (int) - Requested timeout in milliseconds.

		Returns:
			Nothing
		'''
		self.log.debug("setTimeout call")
		# Signature: ErrCode setTimeout(TaskHandle t, const unsigned int timeout);
		self.log.debug("Setting socket timeout to: %s ms", timeout_ms)
		ret = self.dll.setTimeout(self.task_handle, timeout_ms)
		self.__check_ret(ret)

	###############################################################

	def isSerialPortPresent(self):
		'''
		Get whether the remote hardware has a serial port peripheral.

		Returns:
			True if the hardware supports a serial port, False if not.
		'''
		self.log.debug("isSerialPortPresent call")
		# Signature: ErrCode isSerialPortPresent(TaskHandle t, bool* present);
		present = self.ffi.new("bool *", False)
		ret = self.dll.isSerialPortPresent(self.task_handle, present)
		self.__check_ret(ret)
		return present[0]

	def setSerialPortFeature(self, enable, buffer_size = 128):
		'''
		If the remote hardware has a serial port, this call configures it.

		Args:
			enable (bool) Enables/Disables the reception of serial data by the AVMU.
			buffer_size (int) Size of the serial RX buffer to allocate. This can be \
			    any value > 1 and < 255.


		raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Feature_Not_Present`:   if the remote AVMU \
			    does not have a serial port.

		'''
		self.log.debug("setSerialPortFeature call")
		# Signature: ErrCode setSerialPortFeature(TaskHandle t, const bool enable, const unsigned int buffer_size);
		assert (buffer_size < 256)
		self.serial_buf_sz = buffer_size
		ret = self.dll.setSerialPortFeature(self.task_handle, enable, buffer_size)
		self.__check_ret(ret)

	###############################################################

	def isShaftEncoderPresent(self):
		'''
		Get whether the AVMU has support for external shaft encoder inputs.

		Returns:
			(bool) whether the connected AVMU has support for encoders

		'''
		self.log.debug("isShaftEncoderPresent call")
		# Signature: ErrCode isShaftEncoderPresent(TaskHandle t, bool* present);
		present = self.ffi.new("bool *", False)
		ret = self.dll.isShaftEncoderPresent(self.task_handle, present)
		self.__check_ret(ret)
		return present[0]

	def setShaftEncoderFeature(self, enable, resetOnStart=True):
		'''
		If the AVMU supports encoders, this allows you to enable the encoders,
		and optionally reset the cumulative encoder counter.

		Args:
			enable(bool) Tell the hardware to sample the encoders.
			resetOnStart(bool) Reset the accumulated encoder counter in the hardware \
			             on sweep start. If this is not set, the value accumulated from \
			             any previous motion will remain in the accumulator, and be \
			             present when the hardware is started.


		raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Feature_Not_Present`:   if the remote AVMU \
			    does not have encoder support.


		'''
		self.log.debug("setShaftEncoderFeature call")
		# Signature: ErrCode setShaftEncoderFeature(TaskHandle t, const bool enable);
		ret = self.dll.setShaftEncoderFeature(self.task_handle, enable, resetOnStart)
		self.__check_ret(ret)

	###############################################################

	# Note: UNTESTED!
	def configureTddSettings(self,
				tddEnabled        = False,
				nullingEnabled    = False,
				powerAmpState     = False,
				slave             = False,
				attenuatorEnabled = False,
				lnaEnabled        = False,
				attenuatorValue   = 0,
				tx                = 0,
				tx_to_rx1         = 0,
				rx1               = 0,
				rx1_to_rx2        = 0,
				rx2               = 0,
				rx2_to_tx         = 0,
			):
		self.log.debug("configureTddSettings call")
		# Signature: ErrCode setShaftEncoderFeature(TaskHandle t, const bool enable);
		ret = self.dll.configureTddSettings(
			self.task_handle,
			True,
			bool(tddEnabled),
			bool(nullingEnabled),
			bool(powerAmpState),
			bool(slave),
			bool(attenuatorEnabled),
			bool(lnaEnabled),
			bool(attenuatorValue),
			int(tx),
			int(tx_to_rx1),
			int(rx1),
			int(rx1_to_rx2),
			int(rx2),
			int(rx2_to_tx))
		self.__check_ret(ret)

	###############################################################

	def getState(self):

		'''
		 Get the current state of the Task.

		Returns:
			(str) One of 'TASK_RUNNING', 'TASK_STARTED', 'TASK_STOPPED' or 'TASK_UNINITIALIZED'.

		'''
		self.log.debug("getState call")
		# Signature: TaskState getState(TaskHandle t);
		state = self.dll.getState(self.task_handle)
		for state_name, state_val in self.run_state.items():
			if state_val == state:
				return state_name

		raise avmu_exceptions.Avmu_Exception_Wrong_State("State value returned is not known (%s)!" % state)

	#################################################################################
	#        Diagnostics
	#################################################################################

	def getHardwareDetails(self):
		'''
		Get the hardware details for the unit associated with this AvmuInterface instance.

		TODO: VALIDATE THIS!

		Args:
			None

		Returns:
			A dictionary of the HardwareDetails members -> value mappings.  \
			If the Task has not yet been initialized, the returned dict has all values set to 0.

		'''
		self.log.debug("getHardwareDetails call")
		# Signature: HardwareDetails getHardwareDetails(TaskHandle t);
		hardwareDetails = self.dll.getHardwareDetails(self.task_handle)

		ret = {
			"minimum_frequency" : hardwareDetails.minimum_frequency,
			"maximum_frequency" : hardwareDetails.maximum_frequency,
			"maximum_points"    : hardwareDetails.maximum_points,
			"serial_number"     : hardwareDetails.serial_number,

			"band_boundaries"   : [hardwareDetails.band_boundaries[x]
										for x in range(hardwareDetails.number_of_band_boundaries)]
		}
		return ret

	def utilPingUnit(self):
		'''
		Sends an "are you there" message to the unit.

		Note that this function should not be
		called while a frequency sweep is ongoing, because it causes that sweep to prematurely
		halt and respond to this message instead. This is only an issue in multithreaded code or
		when in async mode, as the sync data acquisition functions are blocking. This function
		waits for a reply for the length of time specified by getTimeout() before giving up.

		Note that this can be called from any state, provided an IP and port are present.

		Raises an exception if the unit did not respond, returns nothing otherwise.


		Raises:

			:class:`~avmu.avmu_exceptions.Avmu_Exception_Socket` if there was a problem sending a message
			:class:`~avmu.avmu_exceptions.Avmu_Exception_No_Response` if the unit did not respond to commands
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Missing_Ip` if no IP address has been set
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Missing_Port` if no port has been set

		'''
		self.log.debug("utilPingUnit call")
		# Signature: ErrCode utilPingUnit(TaskHandle t);
		ret = self.dll.utilPingUnit(self.task_handle)
		self.__check_ret(ret)
		self.log.debug("utilPingUnit return")
		return True

	def versionString(self):
		'''
		Returns a string describing the version of the DLL and its components.

		Returns:
			String describing the AVMU DLL components and version numbers.
		'''
		self.log.debug("versionString call")
		# Signature: const char* versionString();
		ret = self.dll.versionString()
		return self.ffi.string(ret).decode("ascii")

	#################################################################################
	#        Utilities
	#################################################################################

	def utilFixLinearSweepLimits(self, startF, endF, npts):
		'''
		Adjusts the start and end of a requested linear sweep with N points such that all
		frequencies in the sweep will land on exactly generateable values, and the inter-point
		spacing is constant across the entire scan. Unequal spacing will cause Doppler noise in
		the data.

		This may move the start and end frequencies of the scan slightly (<1 MHz).

		If the input frequencies are equal, or N is 1, the frequencies are each
		simply adjusted to exactly generateable values.

		TODO: VALIDATE THIS!

		Args:
			startF(float) - Target start frequency for sweep, in Mhz.
			endF(float) - Target end frequency for sweep, in Mhz.
			npts(int) - Number of points to sample, spaced linearly between startFreq and endFreq

		Returns:
			Adjusted start and stop frequencies as a 2-tuple


		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STOPPED state
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Too_Many_Points` if N is larger than \
			                                the maximum allowed (see HardwareDetails)
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Freq_Out_Of_Bounds` if a frequency is \
			                                beyond the allowed min/max. (You can get the min and max from \
			                                the HardwareDetails struct returned by :func:`getHardwareDetails()`)

		'''
		self.log.debug("utilFixLinearSweepLimits call")
		# Signature: ErrCode utilFixLinearSweepLimits(TaskHandle t, double* startFreq, double* endFreq, const unsigned int N);
		startF = self.ffi.new("double *", startF)
		endF   = self.ffi.new("double *", endF)
		ret = self.dll.utilFixLinearSweepLimits(self.task_handle, startF, endF, npts)
		self.__check_ret(ret)
		return startF[0], endF[0]

	def utilNearestLegalFreq(self, freq):
		'''
		Adjusts a requested frequency, in MHz, to the nearest able to be generated by the
		hardware. This is not available in the TASK_UNINITIALIZED state, as it requires knowledge
		of the hardware not read from the AVMU until initialized.

		Args:
			target_freq (float) - Target frequency to be adjusted

		Returns:
			Adjusted `target_freq` Frequency value as a float

			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STOPPED state
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Freq_Out_Of_Bounds` if a frequency is \
			                                beyond the allowed min/max. (You can get the min and max from \
			                                the HardwareDetails struct returned by :func:`getHardwareDetails()`)

		'''
		self.log.debug("utilNearestLegalFreq call")
		# Signature: ErrCode utilNearestLegalFreq(TaskHandle t, double* freq);
		freq   = self.ffi.new("double *", freq)
		ret = self.dll.utilNearestLegalFreq(self.task_handle, freq)
		self.__check_ret(ret)
		return freq[0]

	#################################################################################
	#        Execution
	#################################################################################

	def initialize(self):
		'''
		Attempts to talk to the unit specified by the Task's IP address and port, and download
		its details. If it succeeds the Task enters the TASK_STOPPED state.

		Raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Socket` if there was a problem sending a message
			:class:`~avmu.avmu_exceptions.Avmu_Exception_No_Response` if the unit did not respond to commands
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Missing_Ip` if no IP address has been set
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Missing_Port` if no port has been set
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State`  if the Task is not in the TASK_UNINITIALIZED state
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Bad_Prom`  if the unit returned hardware details that this DLL doesn't understand


		'''
		self.log.debug("initialize call")
		# Signature: ErrCode initialize(TaskHandle t, progress_callback callback, void* user);
		self.log.debug("Initializing remote device.")
		ret = self.dll.initialize(self.task_handle, self.ffi.NULL, self.ffi.NULL)
		self.__check_ret(ret)
		self.log.debug("Remote device initialized.")


	def beginAsync(self):
		'''
		Begin async data collection.
		This call emits the trigger message that will cause the remote hardware to
		immediately begin acquiring frequency data continuously.

		Note that once beginAsync() has been called, you MUST then call measure()
		periodically so that the UDP recieve buffer will not overflow.
		'''
		self.log.debug("beginAsync call")
		# Signature: ErrCode beginAsync(TaskHandle t);
		ret = self.dll.beginAsync(self.task_handle)
		self.__check_ret(ret)

	def broadcastBeginCommand(self, handles=[]):
		'''

		Broadcast a "begin" command to all avmus on the local network. This will start the
		sweep of every avmu on the network at the current position of its internal PC, and
		therefore depends on the avmus having been preconfigured to the proper start addresses
		using beginAsync().

		Args:
			handles (list of AvmuInterface) The list of AVMU AvmuInterface instances to start \
			        in a coordinated manner. Note that if you have all AVMUs in SYNC_IGNORE mode \
			        this will operate fine, but the AVMUs will not be properly synchronized.

		Raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if any of the the tasks are not in the TASK_RUNNING state.
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Task_Array_Invalid` if the passed list is empty (handle_count == 0)

		'''
		self.log.debug("broadcastBeginCommand call")
		# Signature: ErrCode beginAsync(TaskHandle t);
		handles = [other.__getRawTaskHandle() for other in handles]
		# print("Handles:", handles)
		ret = self.dll.broadcastBeginCommand(handles, len(handles))
		self.__check_ret(ret)

	def haltAsync(self):
		'''
		This causes an immediate halt of the async sweep acquisition in the
		remote hardware.

		Any pending data in the UDP recieve buffer will be flushed, and the
		hardware will be returned to the "started" state.

		To resume async data collection after calling haltAsync(),
		simply call beginAsync().
		'''
		self.log.debug("haltAsync call")
		# Signature: ErrCode haltAsync(TaskHandle t);
		ret = self.dll.haltAsync(self.task_handle)
		self.__check_ret(ret)

	def interruptMeasurement(self):
		'''
		Interrupts one of the measurement functions while it is waiting for data.

		Since the measurement functions are blocking in SYNC mode, this function
		must be called from a different thread. This function returns immediately,
		however the measurement function may continue to block for a short additional
		amount of time.

		Raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STARTED state
		'''
		self.log.debug("interruptMeasurement call")
		# Signature: ErrCode interruptMeasurement(TaskHandle t);
		ret = self.dll.interruptMeasurement(self.task_handle)
		self.__check_ret(ret)

	def start(self):
		'''
		Attempts to program the AVMU using the settings stored in the Task object. If it
		succeeds the Task enters the TASK_STARTED state.


		Raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State`  if the Task is not in the TASK_STOPPED state
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Socket` if there was a problem sending a message
			:class:`~avmu.avmu_exceptions.Avmu_Exception_No_Response` if the unit did not respond to commands
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Bad_Prom`  if the unit returned hardware details that this DLL doesn't understand
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Bad_Hop` if the hop rate has not yet been specified
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Missing_Freqs` if the frequencies have not yet been specified
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Prog_Overflow` if the size of the program is too large for the hardware's memory \
				(this can happen if there are too many frequencies)
		'''
		self.log.debug("start call")
		# Signature: ErrCode start(TaskHandle t);
		self.log.info("Starting task.")
		ret = self.dll.start(self.task_handle)
		self.__check_ret(ret)


	def stop(self):
		'''
		 Puts the Task object into the TASK_STOPPED state.

		Raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State`  if the Task is not in the TASK_STARTED state

		'''
		self.log.debug("stop call")
		# Signature: ErrCode stop(TaskHandle t);
		self.log.info("Stopping task.")
		ret = self.dll.stop(self.task_handle)
		self.__check_ret(ret)



	def measure(self):
		'''
		Take a measurement.

		In PROG_SYNC mode, this triggers a measurement, and blocks until its response has
		been fully received and decoded.

		This function does various things depending on the sweep trigger type and the program type.
		Sync mode, internal trigger: run avmu program, block until data is received or timeout
		Sync mode, external trigger: block until data is received or timeout
		Async mode, internal trigger: block until 1 program's worth of data is received or timeout
		Async mode, external trigger: block until 1 program's worth of data is received or timeout

		Note that beginAsync() must be called prior to measure() in async mode.
		The pattern is beginAsync(), measure(), measure(), measure(), ..., haltAsync()

		If the AvmuTask is in async mode (setMeasurementType called with PROG_ASYNC)
		this simply serves to consume any UDP messages generated by the hardware. Note that
		since the hardware asynchronously emits data continuously, you therefore
		*must* call this periodically, or you risk overrunning the socket receive buffer.

		Typically, overrunning the buffer will result in a ``Avmu_Exception_Bytes`` return code, but
		it's theoretically possible to have an entire sweep be dropped (either if it
		fits in a single packet, or if all the packets for the sweep get dropped).

		In this case, the only indicator of data loss will be a non-monotonic sweep
		number in the returned data.

		In general, it's probably ideal to just continualy call this.

		In both cases, measure() places the acquired data in the RX queue, ready
		to be extracted by calling extractSweepData().

		Raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the AvmuInterface is in PROG_SYNC mode, and the AvmuInterface \
		                         state is not TASK_STARTED.
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the AvmuInterface is in PROG_ASYNC mode, and the AvmuInterface \
		                         state is not TASK_RUNNING.

			:class:`~avmu.avmu_exceptions.Avmu_Exception_Bytes` if the received data is corrupted in some manner, or incomplete.
			:class:`~avmu.avmu_exceptions.Avmu_Exception_No_Measured_Paths` if there are no paths added to measure.

		Rare ``Avmu_Exception_Bytes``, particularly when not on a dedicated subnet are
		not entirely unknown, but they shouldn't happen frequently.

		If you encounter large numbers of ``Avmu_Exception_Bytes`` returns, there can be a number of
		causes. TCP Checksum offloading has been known to cause this, as could
		not calling measure() frequently enough. Lastly, check the intervening network
		hardware. You might have a failing switch/hub.

		Note that the AVMU hardware is particularly intolerant of network hubs,
		as its UDP transport does not support data retransmits. Any collisions
		will result in a corrupted sweep (but really, it's 2018+, why are you
		running a network hub?).

		'''
		self.log.debug("measure call")
		# Signature: ErrCode measure(TaskHandle t);
		ret = self.dll.measure(self.task_handle)
		self.__check_ret(ret)


	def getnumberOfEnabledReceivers(self):
		'''
		Returns the number of receivers in the AVMU.
		'''
		self.log.debug("getnumberOfEnabledReceivers call")
		# ErrCode getnumberOfEnabledReceivers(TaskHandle t, int*  num_receivers_enabled);
		present = self.ffi.new("int *", 0)
		ret = self.dll.getnumberOfEnabledReceivers(self.task_handle, present)
		self.__check_ret(ret)
		return present[0]

	def __decodeEnabledReceivers(self, enable_bitmap):
		self.log.debug("__decodeEnabledReceivers call")
		ret = []
		for x in range(8):
			if enable_bitmap & 1 << x:
				ret.append(x)
		return ret

	def getEnabledReceivers(self):
		'''
		Returns a list describing which of the AVMU's receivers will return data.
		'''
		self.log.debug("getEnabledReceivers call")
		# ErrCode getEnabledReceivers(TaskHandle t,         char* enabled_receivers_mask);
		# Use an int8_t because it casts to char cleanly, but
		# doesn't try to act like a bytes character everywhere.
		enable_mask = self.ffi.new("int8_t *", 0)
		ret = self.dll.getEnabledReceivers(self.task_handle, self.ffi.cast("char *", enable_mask))
		self.__check_ret(ret)

		self.active_receivers = self.__decodeEnabledReceivers(enable_mask[0])
		return self.active_receivers

	def __setEnabledReceivers(self, enable_mask):
		self.log.debug("__setEnabledReceivers call")
		# ErrCode setEnabledReceivers(TaskHandle t,         char  enabled_receivers_mask);
		ret = self.dll.setEnabledReceivers(self.task_handle, chr(enable_mask).encode("ascii"))
		self.__check_ret(ret)

		# Query and update the enabled recievers config
		self.getEnabledReceivers()

	def setEnabledReceivers(self, enable_list):
		'''
		Configure which of the receivers in the AVMU will return data.
		'''
		self.log.debug("setEnabledReceivers call")
		valid_receivers = [0, 1, 2, 3]
		assert(all([tmp in valid_receivers for tmp in enable_list]))

		mask = 0
		for item in enable_list:
			mask |= 1 << item
		self.__setEnabledReceivers(mask)

	def __extract_sweep_data_int(self, tx_p_enum, rx_p_enum):
		self.log.debug("__extract_sweep_data_int call")

		point_num = self.getNumberOfFrequencies()
		recs      = self.getEnabledReceivers()

		# print("getEnabledReceivers: ", self.getEnabledReceivers())

		sdat_struct = self.ffi.new("SweepDataStruct *")
		sdat_struct.serial_data_bytes = self.ffi.new("unsigned char [{size}]".format(size=self.serial_buf_sz))

		receiver_arrs = [
				(np.zeros(point_num, dtype=np.float64), np.zeros(point_num, dtype=np.float64))
			for
				dummy
			in
				range(len(recs))
		]

		i_initializer = [self.ffi.cast("double *", tup[0].ctypes.data) for tup in receiver_arrs]
		q_initializer = [self.ffi.cast("double *", tup[1].ctypes.data) for tup in receiver_arrs]

		iarr = self.ffi.new("double*[]", i_initializer)
		qarr = self.ffi.new("double*[]", q_initializer)

		sdat_struct.points.I = iarr
		sdat_struct.points.Q = qarr

		ret = self.dll.extractSweepData(self.task_handle, sdat_struct, tx_p_enum, rx_p_enum)
		self.__check_ret(ret)

		# There's an extra copy here I don't like. Not sure how to work around it, though.

		result = {}
		for x in range(len(recs)):
			result[recs[x]] =np.empty(point_num, dtype=np.complex128)

			result[recs[x]].real = receiver_arrs[x][0]
			result[recs[x]].imag = receiver_arrs[x][1]

		# print("ExtractAllPaths I mean: {}, Q mean: {}".format(np.mean(i), np.mean(q)))

		result_meta = {
			'avmu_ip' : self.getIPAddress(),
			'tx_port'   : self.tx_paths_enum_int[tx_p_enum],
			'tx_port_s' : self.tx_paths_enum_str[tx_p_enum],
			'rx_port'   : self.rx_paths_enum_int[rx_p_enum],
			'rx_port_s' : self.rx_paths_enum_str[rx_p_enum],

			'timestamp_ticks'     : sdat_struct.timestamp_ticks,
			'timestamp_seconds'   : sdat_struct.timestamp_seconds,
			'sweep_number'        : sdat_struct.sweep_number,

			'shaft_encoder_left'  : sdat_struct.shaft_encoder_left,
			'shaft_encoder_right' : sdat_struct.shaft_encoder_right,

			'serial_data_age'   : sdat_struct.serial_data_age,
			'serial_data_bytes' : bytes([sdat_struct.serial_data_bytes[x] for x in range(self.serial_buf_sz)]),

		}
		return result, result_meta



	def __extract_sweep_data_int_old(self, tx_p_enum, rx_p_enum, did_transmit):
		self.log.debug("__extract_sweep_data_int_old call")
		# Signature: ErrCode extractSweepData(TaskHandle t, RFPath path, SweepDataStruct* data);

		point_num = self.getNumberOfFrequencies()
		sdat_struct = self.ffi.new("SweepDataStruct *")
		sdat_struct.serial_data_bytes = self.ffi.new("unsigned char [{size}]".format(size=self.serial_buf_sz))

		i = np.empty(point_num, dtype=np.float64)
		q = np.empty(point_num, dtype=np.float64)


		sdat_struct.points.I = self.ffi.cast("double *", i.ctypes.data)
		sdat_struct.points.Q = self.ffi.cast("double *", q.ctypes.data)

		ret = self.dll.extractSweepData(self.task_handle, sdat_struct, tx_p_enum, rx_p_enum, did_transmit)
		self.__check_ret(ret)

		result = np.empty(point_num, dtype=np.complex128)

		# There's an extra copy here I don't like. Not sure how to work around it, though.
		result.real = i
		result.imag = q
		result_meta = {
			'tx_port'   : self.tx_paths_enum_int[tx_p_enum],
			'tx_port_s' : self.tx_paths_enum_str[tx_p_enum],
			'rx_port'   : self.rx_paths_enum_int[rx_p_enum],
			'rx_port_s' : self.rx_paths_enum_str[rx_p_enum],

			'timestamp_ticks'     : sdat_struct.timestamp_ticks,
			'timestamp_seconds'   : sdat_struct.timestamp_seconds,
			'sweep_number'        : sdat_struct.sweep_number,

			'shaft_encoder_left'  : sdat_struct.shaft_encoder_left,
			'shaft_encoder_right' : sdat_struct.shaft_encoder_right,

			'serial_data_age'   : sdat_struct.serial_data_age,
			'serial_data_bytes' : bytes([sdat_struct.serial_data_bytes[x] for x in range(self.serial_buf_sz)]),

		}
		return result, result_meta


	def extractSweepData(self, tx_path, rx_path):
		'''
		Extract the sweep data for a given path described by a TX port and RX port.

		Note that this interface has the limitation that it does not support multiple measurements
		of the same path within the overall AVMU acqusision frame.

		Args:
			tx_path (str): TX port of the path to extract.
			rx_path (str): RX port of the path to extract.

		Returns:
			- A 2-tuple of containing (data, metadata)
			    data is a numpy complex array with the dimensions of 1 x ``getNumberOfFrequencies()``,
			      where each value bin corresponds to the associated frequency bin in ``getFrequencies()``.
			    metadata is a dict containing the sweep metadata associated with the sweep ``data``.
			      It contains the following key-> value pairs:
				- ``tx_port`` - Transmitting port, as a integer.
				- ``tx_port_s`` - Transmitting port, as a string compatible with ``addPathToMeasure()``.
				- ``rx_port`` - Receiving port, as a integer.
				- ``rx_port_s`` - Receiving port, as a string compatible with ``addPathToMeasure()``.
				- ``timestamp_ticks``   Currently unused. Read as zero.
				- ``timestamp_seconds`` Currently unused. Read as zero.
				- ``sweep_number``      Monotonically increasing counter of the number of sweeps (note:
					sweeps, not frames)
				- ``shaft_encoder_left``  Shaft encoder accumulator for the left-hand shaft encoder.
				    If not enabled, will return 0.
				- ``shaft_encoder_right`` Shaft encoder accumulator for the right-hand shaft encoder.
				    If not enabled, will return 0.
				- ``serial_data_age`` Age of the serial port data. If serial is not enabled, will return 0.
				- ``serial_data_bytes`` Serial data itself, as a bytes array. If not enabled, will be an empty bytes object.

		raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Bad_Path`:   if a path value specified is invalid.

		'''
		self.log.debug("extractSweepData call")
		# Signature: ErrCode extractSweepData(TaskHandle t, RFPath path, SweepDataStruct* data);
		assert tx_path in self.tx_paths, "Invalid path!"
		assert rx_path in self.rx_paths, "Invalid path!"
		tx_p = self.tx_paths[tx_path]
		rx_p = self.rx_paths[rx_path]

		return self.__extract_sweep_data_int(tx_p, rx_p)

	def __extractSweepDataIntPath(self, tx_path_int, rx_path_int):
		self.log.debug("__extractSweepDataIntPath call")
		# Signature: ErrCode extractSweepData(TaskHandle t, RFPath path, SweepDataStruct* data);
		assert tx_path_int in self.tx_paths_int_enum, "Invalid path!"
		assert rx_path_int in self.rx_paths_int_enum, "Invalid path!"
		tx_p = self.tx_paths_int_enum[tx_path_int]
		rx_p = self.rx_paths_int_enum[rx_path_int]

		return self.__extract_sweep_data_int(tx_p, rx_p)

	def extractAllPaths(self):
		'''
		Given a set of measured paths that are unique, extract every path and return them
		as a list.

		This call presumes the user has called ``measure()`` prior to it's invocation.
		If not, it will raise :class:`~avmu.avmu_exceptions.Avmu_Exception_Path_Has_No_Data`:   if you didn't call ``measure()``

		Returns:
			A list of 2-tuples ``(path_info, data)``.

			``path_info`` is a dict containing the following:

				- ``who_is_transmitting``  Which unit is doing the transmitting. This is
				  only relevant in a multi-AVMU context. Single-AVMU setups can ignore it.
				- ``port_is_transmitting``   Which port on the transmitting unit is active. This is
				  only relevant in a multi-AVMU context. Single-AVMU setups can ignore it.
				- ``tx_path``              Which port on the current AVMU is transmitting. For multi AVMU
				  configurations, when the current AVMU is not transmitting, this will be TX_NONE.
				- ``rx_path``              Which port on the current AVMU is receiving.
				- ``receiver_channel``     Which receiver is the dataset for. At the moment, this
				  is ALWAYS 0, as no multi-receiver AVMUs are available.


				In the general single-unit case, you can ignore all the keys other then ``tx_path`` and ``rx_path``.

			``data`` is a dict containing two keys:

				- ``data`` The actual sweep's data. This is directly the ``data`` return component from
				  the ``extractSweepData()`` call.
				- ``meta`` The sweep's metadata. This is directly the ``metadata`` return component from
				  the ``extractSweepData()`` call.

		raises:
			:class:`~avmu.avmu_exceptions.Avmu_Exception_Path_Has_No_Data`:   if you didn't call ``measure()``

		'''
		self.log.debug("extractAllPaths call")
		# Python-only convenience function.
		ret = []
		# print("extractAllPaths() for radar ", self.getIPAddress())
		for who_is_transmitting, port_is_transmitting, tx_path, rx_path in self.measured_paths:
			# print("Extracting path: ", tx_path, rx_path, transmitted)
			rx_dict, meta = self.__extractSweepDataIntPath(tx_path, rx_path)
			for receiver_channel, data in rx_dict.items():
				ret.append((
					{
						'who_is_transmitting'  : who_is_transmitting,
						'port_is_transmitting' : port_is_transmitting,
						'tx_path'              : tx_path,
						'rx_path'              : rx_path,
						'receiver_channel'     : receiver_channel,
					},
					{
						'data' : data,
						'meta' : meta
					}
					))
		return ret



	def setSyncPulseMode(self, sync_mode):
		'''
		Configure the inter-AVMU synchronization pulse mode for the specified AVMU.

		The SyncPulseMode is used to allow coordinated acquisition between
		multiple AVMUs. In coordinated operation, the master unit is set to
		SYNC_GENERATE, and any slave units are set to SYNC_RECEIVE. This
		causes the master to emit sweep start outputs, which are consumed
		by the slave units.

		Note that this requires specialized hardware support, and dedicated
		syncronization wiring.

		Additionally, to properly synchronize, all units must receive their
		start command within 1 ms of each other, which is accomplished via
		the broadcastBeginCommand() call. This also requires the
		shared-communication-infrasturcture provided by the createSharedTask()
		call. All AVMU tasks used in a coordinated acqusition must share
		their internal communication object.

		Args:
			sync_mode (str) One of "SYNC_IGNORE", "SYNC_GENERATE" or "SYNC_RECEIVE"

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State`if the Task is not in the ``TASK_UNINITIALIZED`` or ``TASK_STOPPED`` state

		'''
		self.log.debug("setSyncPulseMode call")
		assert sync_mode in self.sync_pulse_mode

		mode = self.sync_pulse_mode[sync_mode]
		ret = self.dll.setSyncPulseMode(self.task_handle, mode)
		self.__check_ret(ret)

	def getSyncPulseMode(self):
		'''
		Get the current sync pulse mode for this unit.

		Returns:
			Current sync-pulse mode as a string.
		'''

		self.log.debug("getSyncPulseMode call")
		# ErrCode getnumberOfEnabledReceivers(TaskHandle t, int*  num_receivers_enabled);
		sync_mode = self.ffi.new("int *", 0)
		ret = self.dll.getSyncPulseMode(self.task_handle, sync_mode)
		self.__check_ret(ret)

		for key, value in self.sync_pulse_mode.items():
			if value == sync_mode[0]:
				return key

		raise avmu_exceptions.Avmu_Exception("Failed to decode returned sync pulse mode (%s)!" % sync_mode[0])


	def addExclusionBand(self, start_freq, stop_freq):
		'''
		Exclusion bands are used to prevent the AVMU from transmitting in specific
		frequency ranges. This is generally used to "mask out" sensitive RF regions,
		so things like GPS are not negatively affected by the AVMU.

		The AVMU will still take data at points within the exclusion band, but
		the RF output will be disabled.

		Multiple exclusion bands are logically ORed together. Basically, if
		a frequency point falls within *any* exclusion band, it will result in the
		RF output being disabled.

		As such, repeated or overlapping exclusion bands are valid (though
		they are somewhat pointless).

		Note that you cannot add exclusion bands before connecting to an AVMU.

		Note that start_freq must be smaller then stop_freq.

		Args:
			start_freq (float, MHz) - Start of the exclusion band
			stop_freq (float, MHz) - End of the exclusion band (MUST be larger then start_freq)

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STOPPED state

		'''
		self.log.debug("addExclusionBand call")
		# ErrCode addExclusionBand(TaskHandle t, double start_freq, double stop_freq);
		assert stop_freq > start_freq, "The stop frequency must be larger then the start frequency"
		ret = self.dll.addExclusionBand(self.task_handle, start_freq, stop_freq)
		self.__check_ret(ret)

	def clearExclusionBands(self):
		'''
		Clear the internal list of exclusion bands stored in the AvmuInterface.

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Err_Invalid_Parameter` if the parameters do not make sense.
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STOPPED state

		'''
		self.log.debug("clearExclusionBands call")
		# ErrCode clearExclusionBands(TaskHandle t);
		ret = self.dll.clearExclusionBands(self.task_handle)
		self.__check_ret(ret)

	def getExclusionBandCount(self):
		'''
		Get the number of separate exclusion bands configured in the AvmuInterface.

		This is required to enumerate the active exclusion bands.

		Returns:
			exclusion_band_count(int) number of exclusion bands configured.

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STOPPED state

		'''
		self.log.debug("getExclusionBandCount call")
		# ErrCode getExclusionBandCount(TaskHandle t, int* idx);

		exclusion_band_count = self.ffi.new("int *", 0)

		ret = self.dll.getExclusionBandCount(self.task_handle, exclusion_band_count)
		self.__check_ret(ret)

		return exclusion_band_count[0]

	def getExclusionBand(self, band_idx):
		'''
		Get the (start_f_mhz, stop_f_mhz) values for exclusion band band_idx.

		Given a index of 0 <= idx < getExclusionBandCount(), return
		the corresponding exclusion band start/end frequency.

		Return:
			2-tuple of start_f_mhz (double), stop_f_mhz (double)

		Raises:
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Wrong_State` if the Task is not in the TASK_STOPPED state
			 :class:`~avmu.avmu_exceptions.Avmu_Exception_Err_Index_Out_Of_Bounds` if the specified index is not valid.  \
			                                                                      Note that when no exclusion bands are  \
			                                                                      specified, ALL possible values for idx  \
			                                                                      are therefore invalid.
		'''
		self.log.debug("getExclusionBand call")
		# ErrCode getExclusionBand(TaskHandle t, int idx, double* start_freq, double* stop_freq);

		start_f = self.ffi.new("double *", 0)
		stop_f  = self.ffi.new("double *", 0)

		ret = self.dll.getExclusionBand(self.task_handle, band_idx, start_f, stop_f)
		self.__check_ret(ret)

		return start_f[0], stop_f[0]

	def getPreciseTimePerFrame(self):
		'''
		Get the precise time (in seconds) that a Frame will take.

		This function only operates properly when a AVMU is in the started or running states, as
		the sweep program is not computed until the transition to the started state.

		Returns:
			Frame time, as a double, in fractional seconds.
			     If the task is not valid, or in the correct state,
			     the return value is -1.
		'''

		ret = self.dll.getPreciseTimePerFrame(self.task_handle)

		return ret




