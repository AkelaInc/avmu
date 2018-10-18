

'''

Each exception corresponds to the eponymous C error return code, prefixed with ``Avmu_Exception_``.

Note that these exceptions are also available as ``avmu.Avmu_Exception_*``, as they're
star-imported into the main avmu module.

'''


class Avmu_Exception(Exception):
	'''
	Base exception class that all library exceptions inherit from. This
	can be used to easily catch all exceptions that are specifically
	thrown by the ``avmu`` library.
	'''
	pass


class Avmu_Exception_Bad_Atten(Avmu_Exception):
	'''
	Error code indicating the specified attenuation value was not valid.
	'''
	pass
class Avmu_Exception_Bad_Cal(Avmu_Exception):
	'''
	Error code indicating the current calibration is invalid. Only relevant for VNAs.
	'''
	pass
class Avmu_Exception_Bad_Handle(Avmu_Exception):
	'''
	Error code indicating the current handle passed to a DLL function was not valid.

	Generally indicates an internal error. If this occurs repeatedly, please contact support.
	'''
	pass
class Avmu_Exception_Bad_Hop(Avmu_Exception):
	'''
	Error code indicating the specified hop-rate value was not valid.
	'''
	pass
class Avmu_Exception_Bad_Path(Avmu_Exception):
	'''
	Error code indicating the specified path is not allowed, or was invalid.
	'''
	pass
class Avmu_Exception_Bad_Prom(Avmu_Exception):
	'''
	Error code indicating that the AVMU PROM was not in a known format.
	Please contact support if this is a reoccurring issue.
	'''
	pass
class Avmu_Exception_Bytes(Avmu_Exception):
	'''
	Error code indicating the DLL has received an incorrect number of bytes from the AVMU.
	Possibly indicative of a network issue.
	'''
	pass
class Avmu_Exception_Freq_Out_Of_Bounds(Avmu_Exception):
	'''
	Error code indicating one of the specified frequency bounds was beyond the hardware's available range.
	'''
	pass
class Avmu_Exception_Interrupted(Avmu_Exception):
	'''
	Error code indicating that the measurement was asynchronously interrupted from another thread.
	'''
	pass
class Avmu_Exception_No_Response(Avmu_Exception):
	'''
	Error code indicating the remote instrument failed to respond to commands within the current timeout period.
	If this persists, check your network and try power cycling the AVMU.
	'''
	pass
class Avmu_Exception_Missing_Ip(Avmu_Exception):
	'''
	Error code indicating you have not yet specified the IP of the remote device before connecting.
	'''
	pass
class Avmu_Exception_Missing_Port(Avmu_Exception):
	'''
	Error code indicating you have not yet specified the port for the remote device before connecting.
	'''
	pass
class Avmu_Exception_Missing_Hop(Avmu_Exception):
	'''
	Error code indicating you have not yet specified the hop-rate for the remote device before connecting.
	'''
	pass
class Avmu_Exception_Missing_Atten(Avmu_Exception):
	'''
	The switchboard config requires an attenuation value to be specified, and it has not been.
	'''
	pass
class Avmu_Exception_Missing_Freqs(Avmu_Exception):
	'''
	Error code indicating you have not yet specified the frequency endpoints for the remote device before connecting.
	'''
	pass
class Avmu_Exception_Prog_Overflow(Avmu_Exception):
	'''
	Error code indicating the generated program to run on the remote device was larger than it can handle.
	'''
	pass
class Avmu_Exception_Socket(Avmu_Exception):
	'''
	Error code indicating an unknown socket error occured.
	'''
	pass
class Avmu_Exception_Too_Many_Points(Avmu_Exception):
	'''
	Error code indicating you are trying to take more data points than the hardware is capable of.
	'''
	pass
class Avmu_Exception_Wrong_State(Avmu_Exception):
	'''
	Error code indicating the hardware is not in the correct state for the function you are trying to call.
	'''
	pass
class Avmu_Exception_Empty_Prom(Avmu_Exception):
	'''
	Error code indicating the remote device's PROM appears to be empty.
	Power cycle the AVMU, and if the problem persists, contact Akela.
	'''
	pass
class Avmu_Exception_Path_Already_Measured(Avmu_Exception):
	'''
	Error code indicating you are adding a path to measure that you had already added.

	These restrictions have been relaxed in recent releases.
	'''
	pass
class Avmu_Exception_No_Measured_Paths(Avmu_Exception):
	'''
	Error code indicating there are no paths to measure, and the hardware has nothing to do.
	'''
	pass
class Avmu_Exception_Wrong_Program_Type(Avmu_Exception):
	'''
	Error code indicating you are in sync mode and are trying to call an async startup function.
	'''
	pass
class Avmu_Exception_Unknown_Feature(Avmu_Exception):
	'''
	Error code indicating the AVMU's prom indicates it has a hardware feature that this
	version of the DLL doesn't know about. Either indicates you need to update, or the prom is corrupted.
	'''
	pass
class Avmu_Exception_Feature_Not_Present(Avmu_Exception):
	'''
	You are trying to configure a hardware feature not present in the connected AVMU.
	'''
	pass
class Avmu_Exception_No_Attenuator_Present(Avmu_Exception):
	'''
	You are trying to specify an attenuation value on hardware without an attenuator.
	'''
	pass
class Avmu_Exception_Bad_IP_Port(Avmu_Exception):
	'''
	The UDP port you specified is not valid. You must use a port >= 1024 and < 65535
	'''
	pass
class Avmu_Exception_Task_Array_Invalid(Avmu_Exception):
	'''
	The batch-task array parameter appears to not be valid.
	'''
	pass
class Avmu_Exception_Path_Has_No_Data(Avmu_Exception):
	'''
	No data was acquired for the specified path. Either you didn't add the path,
	didn't call measure(), or something else is wrong.
	'''
	pass
class Avmu_Exception_Err_Index_Out_Of_Bounds(Avmu_Exception):
	'''
	 The sweep index/exclusion band you are trying to extract is outside the bounds of the array.
	'''
	pass
class Avmu_Exception_Err_Invalid_Parameter(Avmu_Exception):
	'''
	 One of the specified parameters is not valid.
	 If you are specifying sweep frequency, check your frequency bands.
	'''
	pass
class Avmu_Exception_Err_Prom_Invalid_Feature_Configuration(Avmu_Exception):
	'''
	 The AVMU's prom contains feature flags that are incompatible with each other.
	  Please contact support.
	'''
	pass



## @}
