
#ifndef __AKELA_VNA_DLL_HEADER
#define __AKELA_VNA_DLL_HEADER
		
#ifndef __AKELA_VNA_DLL_H
#define __AKELA_VNA_DLL_H


/** \addtogroup VNA-C-API
 * \authors Steven Hunt (shunt@akelainc.com), Connor Wolf (cwolf@akelainc.com)
 *
 *  \section state-overview Run-state overview
 *
 *  A Task exists in one of four states:
 *  1. Uninitialized (`TASK_UNINITIALIZED`)
 *  2. Stopped (`TASK_STOPPED`)
 *  3. Started (`TASK_STARTED`)
 *  4. Running (`TASK_RUNNING`)
 *
 *  When the object is first created, it is in the uninitialized state.
 *  Here is the state table. The cell content is the new state. Blank cells
 *  mean the action is ignored.
 *
 *                     |--------------------Action------------------------------------------------------|
 * |---Current state---| initialize() | start() | beginAsync() | haltAsync() | stop()  | setIPAddress() |
 * |-------------------|--------------|---------|--------------|-------------|---------|----------------|
 * | uninitialized     | stopped      |         |              |             |         | uninitialized  |
 * | stopped           |              | started |              |             |         | uninitialized  |
 * | started           |              |         | running      |             | stopped |                |
 * | running           |              |         |              | started     | stopped |                |
 *
 *  The initialize() action ensures that the AVMU unit is online and
 *  is responding to commands.  It also downloads the hardware details from
 *  the unit needed to properly program the unit.

 *  The start() action programs the AVMU unit. At this stage the unit is able
 *  to respond to measurement commands.

 *  The stop() action idles the unit.

 *  The setIPAddress() action puts the state back to uninitialized, because
 *  the assumption is that a different VNA unit is going to be targeted.
 *  Hardware details can vary from unit to unit and so those details must be
 *  re-downloaded prior to programming the new unit.
 *  NOTE: any calibration data is marked invalid when the state transitions
 *  to uninitialized. If you would like to use the calibration on a different
 *  unit (or save it for later), see the exportCalibration() function.
 *
 */




//<>/ #if defined(_MSC_VER)
//<>/ 	#define __declspec(dllimport)              __declspec( dllimport )
//<>/ 	#define __declspec(dllimport)_CONSTANT_DEF extern __declspec(dllimport)
//<>/ #elif defined(LINUX)
//<>/ 	#define __declspec(dllimport)              extern
//<>/ 	#define __declspec(dllimport)_CONSTANT_DEF
//<>/ #else
//<>/ 	#error "Unknown platform! Cannot continue!"
//<>/ #endif


/** \addtogroup VNA-C-API
 *  @{
 */


// <<<<<< CPP WRAP START
	#ifdef __cplusplus
		extern "C" {
	#endif
// CPP WRAP END >>>>>>>>


	
// Common include-guards
#ifndef __AKELA_VECTOR_MEASUREMENT_DLL_COMMON_H
#define __AKELA_VECTOR_MEASUREMENT_DLL_COMMON_H

	

	


	/**
	 * @brief Opaque type for containing the parameters and associated
	 *        resources for interfacing with a single AVMU.
	 *
	 *        One piece of software can have multiple tasks open at
	 *        any one time, though having multiple tasks for the same
	 *        AVMU simultaneously can cause undetermined behaviour.
	 *        At any time, there should only ever be one non-`TASK_UNINITIALIZED`
	 *        task for a single AVMU.
	 *
	 */
	typedef struct task_t task_container;
	typedef task_container* TaskHandle;

	/** \addtogroup ErrorCodes
	 *  @brief Potential error-codes API calls can return.
	 *
	 *  @{
	 */
	/**
	 * Error-Code value type. Treat this as an opaque type.
	 */
	typedef int ErrCode;
	__declspec(dllimport) ErrCode ERR_OK;                                   //!< Return "error" code indicating no error occured.
	__declspec(dllimport) ErrCode ERR_BAD_ATTEN;                            //!< Error code indicating the specified attenuation value was not valid.
	__declspec(dllimport) ErrCode ERR_BAD_CAL;                              //!< Error code indicating the current calibration is invalid.
	__declspec(dllimport) ErrCode ERR_BAD_HANDLE;                           //!< Error code indicating the current handle passed to a DLL function was not valid.
	__declspec(dllimport) ErrCode ERR_BAD_HOP;                              //!< Error code indicating the specified hop-rate value was not valid.
	__declspec(dllimport) ErrCode ERR_BAD_PATH;                             //!< Error code indicating the specified path is not allowed, or was invalid.
	__declspec(dllimport) ErrCode ERR_BAD_PROM;                             //!< Error code indicating that the AVMU PROM was not in a known format.  Please contact support if this is a reoccuring issue
	__declspec(dllimport) ErrCode ERR_BYTES;                                //!< Error code indicating the DLL has received an incorrect number of bytes from the AVMU. Possibly indicative of a network issue.
	__declspec(dllimport) ErrCode ERR_EMPTY_PROM;                           //!< Error code indicating the remote device's PROM appears to be empty. Power cycle the AVMU, and if the problem persists, contact Akela.
	__declspec(dllimport) ErrCode ERR_FEATURE_NOT_PRESENT;                  //!< You are trying to configure a hardware feature not present in the connected AVMU.
	__declspec(dllimport) ErrCode ERR_FREQ_OUT_OF_BOUNDS;                   //!< Error code indicating one of the specified frequency bounds was beyong the hardware's available range.
	__declspec(dllimport) ErrCode ERR_INTERRUPTED;                          //!< Error code indicating that the measurement was asynchronously interrupted from another thread.
	__declspec(dllimport) ErrCode ERR_MISSING_FREQS;                        //!< Error code indicating you have not yet specified the frequency endpoints for the remote device before connecting.
	__declspec(dllimport) ErrCode ERR_MISSING_HOP;                          //!< Error code indicating you have not yet specified the hop-rate for the remote device before connecting.
	__declspec(dllimport) ErrCode ERR_MISSING_IP;                           //!< Error code indicating you have not yet specified the IP of the remote device before connecting.
	__declspec(dllimport) ErrCode ERR_BAD_IP_PORT;                          //!< The UDP port you specified is not useable. You must use a port >= 1024 and < 65535
	__declspec(dllimport) ErrCode ERR_MISSING_PORT;                         //!< Error code indicating you have not yet specified the port for the remote device before connecting.
	__declspec(dllimport) ErrCode ERR_NO_PATHS_MEASURED;                    //!< Error code indicating there are no paths to measure, and the hardware has nothing to do.
	__declspec(dllimport) ErrCode ERR_NO_RESPONSE;                          //!< Error code indicating the remote instrument failed to respond to commands within the current timeout period.
	__declspec(dllimport) ErrCode ERR_PATH_ALREADY_MEASURED;                //!< Error code indicating you are adding a path to measure that you had already added.
	__declspec(dllimport) ErrCode ERR_PROG_OVERFLOW;                        //!< Error code indicating the generated program to run on the remote device was larger then it can handle.
	__declspec(dllimport) ErrCode ERR_SOCKET;                               //!< Error code indicating an unknown socket error occured.
	__declspec(dllimport) ErrCode ERR_TOO_MANY_POINTS;                      //!< Error code indicating you are trying to take more data points then the hardware is capable of.
	__declspec(dllimport) ErrCode ERR_UNKNOWN_FEATURE;                      //!< Error code indicating the AVMU's prom indicates it has a hardware feature that this
	                                                             //!< version of the DLL doesn't know about. Either indicates you need to update, or the prom is corrupted.
	__declspec(dllimport) ErrCode ERR_WRONG_PROGRAM_TYPE;                   //!< Error code indicating you are in sync mode and are trying to call an async startup function.
	__declspec(dllimport) ErrCode ERR_WRONG_STATE;                          //!< Error code indicating the hardware is not in the correct state for the function you are trying to call.
	__declspec(dllimport) ErrCode ERR_MISSING_ATTEN;                        //!< The switchboard config requires an attenuation value to be specified, and it has not.
	__declspec(dllimport) ErrCode ERR_NO_ATTEN_PRESENT;                     //!< You are trying to specify an attenuation value on hardware without an attenuator.
	__declspec(dllimport) ErrCode ERR_TASK_ARRAY_INVALID;                   //!< The passed batch-task array appears to not be valid.
	__declspec(dllimport) ErrCode ERR_PATH_HAS_NO_DATA;                     //!< No data was acquired for the specified path. Either you didn't add the path, didn't call measure(), or something else is wrong.
	__declspec(dllimport) ErrCode ERR_INDEX_OUT_OF_BOUNDS;                  //!< the sweep index/exclusion band you are trying to extract is outside the bounds of valid values.
	__declspec(dllimport) ErrCode ERR_INVALID_PARAMETER;                    //!< One of the specified parameters is not valid. If you are specifying sweep frequency, check your frequency bands.
	__declspec(dllimport) ErrCode ERR_PROM_INVALID_FEATURE_CONFIGURATION;   //!< The AVMU's prom contains feature flags that are incompatible. Please contact support


	/** @}*/


	/** \addtogroup HopRateSettings
	 *  @brief Settings for the hop-rate (e.g. time spent sampling each
	 *         frequency point) in a sweep.
	 *
	 *         Faster hop rates result in lower dynamic range (but faster sweeps).
	 *
	 *  @{
	 */

	/**
	 * Hop-Rate value type. Treat this as an opaque type.
	 */
	typedef int HopRate;

	__declspec(dllimport) HopRate HOP_UNDEFINED;  //!< Hop rate not set yet
	#ifdef __declspec(dllimport)  // Only export for Avmus, the VNA doesn't support it.
		__declspec(dllimport) HopRate HOP_90K;  //!< This rate is currently unsupported but may be enabled in the future 90K Pts/second
	#endif
	__declspec(dllimport) HopRate HOP_45K;  //!< Hop rate of 45K points/second
	__declspec(dllimport) HopRate HOP_30K;  //!< Hop rate of 30K points/second
	__declspec(dllimport) HopRate HOP_15K;  //!< Hop rate of 15K points/second
	__declspec(dllimport) HopRate HOP_7K;   //!< Hop rate of 7K points/second
	__declspec(dllimport) HopRate HOP_3K;   //!< Hop rate of 3K points/second
	__declspec(dllimport) HopRate HOP_2K;   //!< Hop rate of 2K points/second
	__declspec(dllimport) HopRate HOP_1K;   //!< Hop rate of 1K points/second
	__declspec(dllimport) HopRate HOP_550;  //!< Hop rate of 550 points/second
	__declspec(dllimport) HopRate HOP_312;  //!< Hop rate of 312 points/second
	__declspec(dllimport) HopRate HOP_156;  //!< Hop rate of 156 points/second
	__declspec(dllimport) HopRate HOP_78;   //!< Hop rate of 78 points/second
	__declspec(dllimport) HopRate HOP_39;   //!< Hop rate of 39 points/second
	__declspec(dllimport) HopRate HOP_20;   //!< Hop rate of 20 points/second
	/** @}*/


	/** \addtogroup TaskState
	 *  @brief Available task states.
	 *
	 *  @{
	 */
	/**
	 * Task state value type. Treat this as an opaque type.
	 * see @ref state-overview for more details of what the different
	 * states mean.
	 */
	typedef int TaskState;
	__declspec(dllimport) TaskState TASK_UNINITIALIZED; //!< Task state of uninitialized
	__declspec(dllimport) TaskState TASK_STOPPED;       //!< Task state of stopped
	__declspec(dllimport) TaskState TASK_STARTED;       //!< Task state of started
	__declspec(dllimport) TaskState TASK_RUNNING;       //!< Task state of running

	/** @}*/
	/** \addtogroup Acquisition Type
	*  @brief Acquisition mode (synchronous, asynchronous) for the current acquisition
	*
	*  @{
	*/
	/**
	* RF path selector type. Treat this as an opaque type.
	*/
	typedef int ProgramType;

	__declspec(dllimport) ProgramType PROG_ASYNC;  //!< Asynchronous acquisition mode
	__declspec(dllimport) ProgramType PROG_SYNC;   //!< Synchronous acquisition mode


	/**
	 * Switchboard type.
	 */
	typedef int SwitchboardType;
	__declspec(dllimport) SwitchboardType SWITCHBOARD_SIMPLE_4_PORT_SWITCH;
	__declspec(dllimport) SwitchboardType SWITCHBOARD_TDD_4_PORT_SWITCH;
	__declspec(dllimport) SwitchboardType SWITCHBOARD_NO_SWITCH_BOARD;
	__declspec(dllimport) SwitchboardType SWITCHBOARD_SIMPLE_8_PORT_SWITCH;
	__declspec(dllimport) SwitchboardType SWITCHBOARD_S_PARAMETER_SWITCH;

	/** @}*/


	/**
	 * HardwareDetails struct.
	 * This struct is used to encapsulate the capabilities of a specific AVMU.
	 *
	 * Values for minimum and maximum frequencies, as well as the band boundaries
	 * are all in megahertz.
	 */
	typedef struct HardwareDetails_t
	{
		/** Minimum frequency, in Mhz, that the AVMU can measure. */
		int minimum_frequency;
		/** Maximum frequency, in Mhz, that the AVMU can measure. */
		int maximum_frequency;
		/** Maximum number of points the AVMU can sample in a single acquisition. */
		int maximum_points;
		/** Serial number of connected AVMU */
		int serial_number;
		/**
		 * Band boundaries in the connected AVMU. Highest frequency first, values in Mhz.
		 * Array size is specified in the `number_of_band_boundaries` struct member.
		 */
		int band_boundaries[8];

		/** Number of band boundaries in `band_boundaries` struct member. */
		int number_of_band_boundaries;

		/** Switchboard type of the connected hardware */
		SwitchboardType swbd_type;

		struct hardware_features_t
		{
			/** Does the connected AVMU have encoder inputs */
			bool has_encoders;
			/** Does the connected AVMU have a serial rx port */
			bool has_serial_port;
			/** Does the connected AVMU have a hardware attenuator */
			bool has_attenuators;
			/** Does the connected AVMU have multiple receivers */
			bool has_multiple_receivers;
			/** Does the connected AVMU have a scan-trigger input */
			bool has_scan_trigger_in;
			/** Does the connected AVMU have a scan-trigger output */
			bool has_scan_trigger_out;

		} hardware_features;

	} HardwareDetails;

	/**
	 * Container struct for passing IQ data sets around.
	 * The `I` and `Q` members are pointers to caller-allocated
	 * arrays of the requisite type (double, in this case).
	 */

	typedef struct ComplexDataStruct_t
	{
		/** In-phase component value array */
		double **I;
		/** Quadrature component value array */
		double **Q;
	} ComplexDataStruct;


	/**
	 * @brief Struct that contains the sweep-specific information for a single
	 *        sweep.
	 *
	 */
	typedef struct SweepDataStruct_t
	{
		/** In-phase component value array */
		ComplexDataStruct points;

		/* Shaft encoder contents */
		unsigned int shaft_encoder_left;     //!< Shaft encoder readout for the "left" shaft.
		unsigned int shaft_encoder_right;    //!< Shaft encoder readout for the "right" shaft.

		/* Shaft encoder contents */
		unsigned int  serial_data_age;       //!< The "age" of the recieved serial data. Incremented by a clock (TODO: Fixme!)
		unsigned char* serial_data_bytes;    //!< Recieved serial data as a char array. Fixed length array of

		/* Sweep metadata components */
		unsigned int  timestamp_ticks;
		double timestamp_seconds;
		unsigned int  packet_num;
		unsigned int  sweep_number;
		unsigned int  frame_num;

	} SweepDataStruct;

	/**
	 * @brief This is the method signature for the callback function
	 *        passed to the `initialize()` function.
	 *
	 *        The `initialize()` function takes a callback because it can
	 *        take >30 seconds to execute while it downloads the embedded
	 *        calibration from the AVMU.
	 *
	 *        As such, the callback is called periodically while retreiving the
	 *        cal data so the process can be presented to the user.
	 *
	 * @param progressPercent Percentage of the download, from 0 - 100 %.
	 *                        Value is an integer.
	 *                        The callback may be called multiple times with the same
	 *                        progress percentage.
	 * @param user "user data". This is a void pointer that is passed in to the
	 *             `initialize()` function, and then simply passed through to
	 *             the callback every time it's called. It's intention is to
	 *             allow a reference to any relevant user-code to be made available
	 *             to the callback, so it could potentially update some external
	 *             state.
	 *             Set as NULL if unused.
	 *
	 * @return Continue value. If the callback returns false, the cal download will halt
	 *                  immediately and `initialize()` will return ERR_INTERRUPTED.
	 *                  If the callback returns true, the download will continue.
	 *
	 */
	typedef bool (*progress_callback)(int progressPercent, void* user); // return false to cancel



	/**
	 * @brief Returns a string describing the version of the DLL and its components
	 * @return Human-readable ASCII string pointer.
	 */
	__declspec(dllimport) const char* versionString();

	/**
	 * @brief Creates a new Task object and returns a handle to it.
	 *        This handle is required by all of the other API
	 *        functions. The returned object is in the
	 *        TASK_UNINITIALIZED state.
	 * @return new task handle
	 */
	__declspec(dllimport) TaskHandle createTask();

	/**
	 * @brief Deletes the Task object. If the caller does not do this, the handle memory will leak.
	 *
	 * @param t Task to delete
	 */
	__declspec(dllimport) void deleteTask(TaskHandle t);

	/**
	 * @brief Attempts to talk to the unit specified by the Task's IP address, and download
	 *        its details. If it succeeds the Task enters the TASK_STOPPED state.
	 *
	 *        This call can take a fair bit of time, up to 30 seconds <-> 1 minte.
	 *        For that purpose, a callback interface is provided
	 *
	 * @param t Handle for the current task
	 * @param callback User-provided callback function. Method signature must match
	 *                 \ref progress_callback. See \ref progress_callback for further
	 *                 details of the callback system.
	 *                 Set to NULL if no callback is required.
	 * @param user user-data provided to the callback function. See \ref progress_callback
	 *             for further description.
	 *             Not used if the \ref progress_callback param is NULL;
	 * @return Call status - Possible return values:
	 *          - ERR_OK if all went according to plan
	 *          - ERR_MISSING_IP if an IP has not been specified
	 *          - ERR_MISSING_PORT if a port has not been specified
	 *          - ERR_SOCKET if there was a problem setting up the UDP socket or sending a message
	 *          - ERR_NO_RESPONSE if the unit did not respond to commands
	 *          - ERR_BAD_PROM if the unit returned hardware details that this DLL doesn't understand
	 *          - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED state
	 *          - ERR_INTERRUPTED if the initialization was cancelled from the callback.
	 */
	__declspec(dllimport) ErrCode initialize(TaskHandle t, progress_callback callback = 0, void* user = 0);

	/**
	 * @brief Attempts to program the AVMU using the settings stored in the Task object. If it
	 *        succeeds the Task enters the TASK_STARTED state.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *
	 * @return Call status - Possible return values:
	 *          - ERR_OK if all went according to plan
	 *          - ERR_SOCKET if there was a problem sending a message
	 *          - ERR_NO_RESPONSE if the unit did not respond to commands
	 *          - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	 *          - ERR_MISSING_HOP if the hop rate has not yet been specified
	 *          - ERR_MISSING_ATTEN if the attenuation has not yet been specified (if attenuation is required)
	 *          - ERR_MISSING_FREQS if the frequencies have not yet been specified
	 *          - ERR_PROG_OVERFLOW if the size of the program is too large for the hardware's memory
	 *                    (this can happen if the AVMU is asked to sample too many frequency points)
	 */
	__declspec(dllimport) ErrCode start(TaskHandle t);

	/**
	 * @brief Puts the Task object into the TASK_STOPPED state.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *           - ERR_OK if all went according to plan
	 *           - ERR_WRONG_STATE if the Task is not in the TASK_STARTED state
	 */
	__declspec(dllimport) ErrCode stop(TaskHandle t);


	/**
	 * @brief Sets the IPv4 address on which to communicate with the unit.
	 *        The ipv4 parameter is copied into the Task's memory.
	 *        On success the Task's state will be TASK_UNINITIALIZED.
	 *        Example: setIPAddress(t, "192.168.1.197");
	 *
	 * @param t Handle for the current task
	 * @param ipv4 ASCII String IP representation, e.g. "192.168.1.207", etc...
	 *
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - ERR_MISSING_IP if the pointer is null
	 *       - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED or TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode setIPAddress(TaskHandle t, const char* ipv4);

	/**
	 * @brief Sets the port on which to communicate with the unit.
	 *        The value of `port` MUST be > 1024, as 1024 is reserved
	 *        for broadcast operations. Additionally, the maximum value
	 *        for the port is 1279 (1024 + 256).
	 *        Note that for multi-unit configurations, each unit must be
	 *        assigned a unique port > 1024 (the AVMU units listen on all
	 *        ports, but only respond to broadcast commands on port 1024).
	 *        On success, the Task's state will be TASK_UNINITIALIZED.
	 *
	 * @param t Handle for the current task
	 * @param port integer port number
	 *
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED or TASK_STOPPED state
	 *       - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED or TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode setIPPort(TaskHandle t, const int port);

	/**
	 * @brief Sets the default time to wait, in milliseconds, for a unit to
	 *        reply to a command before giving up and returning an ERR_NO_RESPONSE
	 *        condition. For the measurement functions, this is the amount
	 *        of time to wait beyond the expected sweep time. When a Task is
	 *        created, the timeout value defaults to 100.
	 *
	 *   TODO: VALIDATE THIS - What happens if passed 0?
	 *
	 * @param t Handle for the current task
	 * @param timeout timeout in milliseconds
	 *
	 * @return Always returns ERR_OK.
	 */
	__declspec(dllimport) ErrCode setTimeout(TaskHandle t, const unsigned int timeout);


	/**
	* @brief Set the frequencies to measure during each sweep. Units are MHz. The freqs
	*        parameter is an array of length N. Note that the AVMU frequency generation
	*        hardware has fixed precision and so the generated frequency may not be exactly
	*        equal to the requested frequency. This function silently converts all requested
	*        frequencies to frequencies that can be exactly generated by the hardware.
	*        This has important implications for doppler noise when doing a linear sweep.
	*        AKELA recommends using the function utilFixLinearSweepLimits() to ensure
	*        every frequency is exactly generateable and that the frequencies are equally
	*        spaced. Use the getFrequencies() function to get the actual frequencies being
	*        generated.
	*
	* @param t Handle for the current task
	* @param freqs array of frequencies to sample, in MHz
	* @param N Length of `freqs` array.
	* @return Call status - Possible return values:
	*       - ERR_OK if all went according to plan
	*       - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	*       - ERR_FREQ_OUT_OF_BOUNDS if a frequency is beyond the allowed min/max. (You can get
	*         the min and max from the HardwareDetails struct returned by getHardwareDetails())
	*       - ERR_TOO_MANY_POINTS if N is larger than the maximum allowed (see HardwareDetails)
	*/
	__declspec(dllimport) ErrCode setFrequencies(TaskHandle t, const double* freqs, const unsigned int N);

	/**
	 * @brief Set the frequency hopping rate. See the values defined in the "HopRate" type above.
	 *
	 * @param t Handle for the current task
	 * @param rate HopRate as member of HopRate type.
	 *
	 * @return Call status - Possible return values:
	 *      - ERR_OK if all went according to plan
	 *      - ERR_BAD_HOP if there was something wrong with the hop rate parameter
	 *      - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED or TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode setHopRate(TaskHandle t, const HopRate rate);

	/**
	 * @brief Toggle the measuring of the connected shaft encoder feature, if present.
	 *
	 * @param t Handle for the current task
	 * @param enable Should the shaft-encoders be sampled every sweep.
	 * @param reset_on_start Should the shaft encoder value be reset at the start of the acquisition,
	 * 						 or should the value be preserved across multiple acquisitions.
	 *
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - TODO: More
	 */
	__declspec(dllimport) ErrCode setShaftEncoderFeature(TaskHandle t, const bool enable, const bool reset_on_start);

	/**
	 * @brief Configure the serial port feature.
	 *
	 * @param t Handle for the current task
	 * @param enable Should the serial port hardware capture data, and associate it with the sweep data.
	 * @param buffer_size The number of bytes you expect to recieve with the serial port. The AVMU's serial interface is gap-delimited, and
	 *            not circular buffered. If multiple messages are recieved during a sweep, only the last message will
	 *            be forwarded to the application code.
	 *
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - TODO: More
	 */
	__declspec(dllimport) ErrCode setSerialPortFeature(TaskHandle t, const bool enable, const unsigned int buffer_size);

	/**
	 * @brief Set the measurement type (synchronous or asynchronous).
	 *        Defaults to synchonous (PROG_SYNC)
	 *
	 * @param t Handle for the current task
	 * @param type One of the ProgramType types (PROG_ASYNC or PROG_SYNC).
	 *
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - TODO: More
	 */
	__declspec(dllimport) ErrCode setMeasurementType(TaskHandle t, const ProgramType type);

	/**
	 * @brief Return the current measurement ProgramType type..
	 *
	 * @param t Handle for the current task
	 * @return One of the ProgramType types (PROG_ASYNC or PROG_SYNC)
	 */
	__declspec(dllimport) ProgramType getMeasurementType(TaskHandle t);

	/**
	 * @brief Get the current state of the Task object. Returns one of the values defined above.
	 *
	 * @param t Handle for the current task
	 * @return A value from the TaskState state list
	 */
	__declspec(dllimport) TaskState getState(TaskHandle t);

	//
	/**
	 * @brief Get the current time to wait for the unit to reply to commands. When a Task is first created, this will default to 100 ms.
	 *
	 * @param t Handle for the current task
	 * @return current timeout in milliseconds
	 */
	__declspec(dllimport) unsigned int getTimeout(TaskHandle t);

	/**
	 * @brief Get the current AVMU IP address for the Task object.
	 *        When no IP has yet been set, this will return a NULL
	 *        char*.
	 *
	 * @param t Handle for the current task
	 * @return char* to string containing the AVMU IP address. NULL if not set.
	 */
	__declspec(dllimport) const char* getIPAddress(TaskHandle t);

	/**
	 * @brief Get the current port for IP communications.
	 *        When uninitialized, this will default to 0.
	 *
	 * @param t Handle for the current task
	 * @return current port number
	 */
	__declspec(dllimport) int getIPPort(TaskHandle t);

	//
	/**
	 * @brief Get the frequency hopping rate associated with this Task object.
	 *        If no rate has yet been set, this function returns HOP_UNDEFINED.
	 *
	 * @param t Handle for the current task
	 * @return HopRate for the Task `t` in question.
	 */
	__declspec(dllimport) HopRate getHopRate(TaskHandle t);

	/**
	 * @brief Get the number of frequency points for the sweep configured for
	 *        Task `t`. If no frequencies have been set, this function returns 0.
	 *
	 * @param t Handle for the current task
	 * @return Number of frequency points in Task `t`.
	 */
	__declspec(dllimport) unsigned int getNumberOfFrequencies(TaskHandle t);

	/**
	* @brief Get a list containing the actual frequencies the hardware will sample for
	*        the configured sweep in task `t`. Units are MHz.
	*
	*        The actual frequency points can differ from the requested frequency points
	*        because the hardware has fixed precision, and cannot achieve every arbitrary
	*        frequency value within its tunable bands. The values in this list are the
	*        requested frequency points after snapping them to the closest achievable
	*        frequency.
	*
	* @param t Handle for the current task
	* @param freqs Pointer to a array into which the frequency values are to be
	* 			   written. The user must ensure that this buffer is at keast
	* 			   getNumberOfFrequencies() in size.
	* @param freqs_sz The size of the freqs array.
	* @return ERR_OK or ERR_BAD_HANDLE depending on handle validity
	*/
	__declspec(dllimport) ErrCode getFrequencies(TaskHandle t, double* freqs, int freqs_sz);

	/**
	 * @brief Get the hardware details for the unit associated with
	 *        Task `t`. If the Task has not yet been initialized, the
	 *        returned struct has all values set to 0.
	 *
	 * @param t Handle for the current task
	 * @return `HardwareDetails` containing the details of the connected
	 *                           hardware (if initialized), else zeroes.
	 */
	__declspec(dllimport) HardwareDetails getHardwareDetails(TaskHandle t);

	//
	/**
	 * @brief Adjusts a requested frequency, in MHz, to the nearest able to be generated by the AVMU
	 *        hardware. This is not available in the TASK_UNINITIALIZED state.
	 *
	 * @param t Handle for the current task
	 * @param freq Requested frequency value, which will be modified to the nearest
	 *             frequency the hardware can achieve.
	 *
	 * @return Call status - Possible return values:
	 *            - ERR_OK if all went according to plan
	 *            - ERR_WRONG_STATE if the Task is in the TASK_UNINITIALIZED state
	 *            - ERR_FREQ_OUT_OF_BOUNDS if the frequency is beyond the allowed min/max
	 */
	__declspec(dllimport) ErrCode utilNearestLegalFreq(TaskHandle t, double* freq);

	/**
	 * @brief Adjusts the start and end of a requested linear sweep with N points such
	 *        that all frequencies in the sweep will land on exactly generateable values.
	 *
	 *        This is important so that the frequency spacing between all points is
	 *        identical. Unequal spacing can cause doppler noise in your data.
	 *
	 *        If the input frequencies are equal, or N is 0 or 1, the frequencies are each adjusted to exactly generateable values.
	 *
	 * TODO: More units to validate!
	 *
	 * @param t Handle for the current task
	 * @param startFreq Start frequency (in Mhz)
	 * @param endFreq Stop frequency (in Mhz)
	 * @param N Number of frequencies
	 * @return Call status - Possible return values:
	 *             - ERR_OK if all went according to plan
	 *             - ERR_WRONG_STATE if the Task is in the TASK_UNINITIALIZED state
	 *             - ERR_FREQ_OUT_OF_BOUNDS if one of the bounds is beyond the allowed min/max. (You can get
	 *               the min and max from the HardwareDetails struct returned by getHardwareDetails())
	 *             - ERR_TOO_MANY_POINTS if N is larger than the maximum allowed (see HardwareDetails)
	 */
	__declspec(dllimport) ErrCode utilFixLinearSweepLimits(TaskHandle t, double* startFreq, double* endFreq, const unsigned int N);

	/**
	 * @brief Sends an "are you there" message to the unit. Note that this function should not be
	 *        called while a frequency sweep is ongoing, because it causes that sweep to prematurely
	 *        halt and respond to this message instead. This is only an issue in multithreaded code,
	 *        since the data acquisition functions are blocking. This function waits for a reply for
	 *        the length of time specified by getTimeout() before giving up.
	 *
	 *        Note that this can be called from any state, provided an IP and port are present.
	 *
	 * @param tries Number of pings to send before concluding a unit is not responding.
	 *              The call will block for at most tries * timeout milliseconds.
	 *              Note that certain states can cause the hardware to be unable to 
	 *              respond to the first ping, so tries > 1 is generally recommended.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *        - ERR_OK if all went according to plan
	 *        - ERR_SOCKET if there was a problem sending a message
	 *        - ERR_NO_RESPONSE if the unit did not respond to commands
	 *        - ERR_MISSING_IP if no IP address has been set
	 *        - ERR_MISSING_PORT if no port has been set
	 */
	__declspec(dllimport) ErrCode utilPingUnit(TaskHandle t, int tries = 5);


	/**
	* @brief Turn off the AVMU's internal +-5V supplies for the RF section. This should significantly
	*        reduce the AVMU's idle power consumption.
	*        Note that the AVMU will automatically be powered up by any attempt to start a scan,
	*        or a disconnect/reconnect event.
	*        When resuming operation after being in a low-power state, the first returned sweep
	*        may have higher noise levels or not be valid, as the power supplies can take several
	*        milliseconds to enable and stabilize.
	*        The AVMU must be connected, but not active for this to occur, corresponding to the
	*        hardware being in the TASK_STARTED or TASK_STOPPED states.
	*
	* @return Possible return values:
	*        	ERR_OK if the AVMU was powered down
	*        	ERR_WRONG_STATE if the AVMU was not in either TASK_STARTED or TASK_STOPPED states
	*        	ERR_BYTES if the AVMU did not response correctly.
	*
	*/
	__declspec(dllimport) ErrCode utilEnterLowPowerState(TaskHandle t);

	/**
	 * @brief Generates a linear sweep with the requested parameters. Note that the start and end
	 *        frequency will be adjusted as documented in utilFixLinearSweepLimits() so that all
	 *        frequency points fall on exactly generateable values. This function internally calls
	 *        setFrequencies() with the resulting array. The caller can retrieve the frequency list
	 *        with the getFrequencies() function. Since it changes the frequencies this function
	 *        is only available in the TASK_STOPPED state.
	 *
	 *        If `startFreq` == `endFreq`, the hardware will effectively be placed in zero-span
	 *        mode, as it will repeatedly sample the same frequency for the duration of the
	 *        sweep. This is a valid operating mode.
	 *
	 * @param t Handle for the current task
	 * @param startFreq Start frequency of sweep in Mhz
	 * @param endFreq End frequency of sweep in Mhz
	 * @param N Number of points to sample.
	 * @return Call status - Possible return values:
	 *        - ERR_OK if all went according to plan
	 *        - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	 *        - ERR_FREQ_OUT_OF_BOUNDS if one of the bounds is beyond the allowed min/max. (You can get
	 *          the min and max from the HardwareDetails struct returned by getHardwareDetails())
	 *        - ERR_TOO_MANY_POINTS if N is larger than the maximum allowed (see HardwareDetails)
	 */
	__declspec(dllimport) ErrCode utilGenerateLinearSweep(TaskHandle t, const double startFreq, const double endFreq, const unsigned int N);



	/**
	 * @brief Interrupts one of the measurement functions while it is waiting for
	 *        data. Since the measurement functions are blocking, this function
	 *        must be called from a different thread. This function returns
	 *        immediately, however the measurement function may continue to block
	 *        for a short additional amount of time.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *      - ERR_OK if all went according to plan
	 *      - ERR_WRONG_STATE if the Task is not in the TASK_STARTED state
	 */
	__declspec(dllimport) ErrCode interruptMeasurement(TaskHandle t);


	/**
	 * @brief Determines if the sweep timer is sent at the beginning of each frame.
	 * The sweep timer is a 32.768 MHz/256 clock which increments a 32 bit register.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *      - ERR_OK if all went according to plan
	 *      - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	*/
	__declspec(dllimport) ErrCode setSendSweepTimer(TaskHandle t, bool send_timer);
	__declspec(dllimport) ErrCode getSendSweepTimer(TaskHandle t, bool* val);


	/**
	 * @brief Determines if the frame counter is reset when the avmu is started.
	 * if false, the existing value is preserved. If true, it is reset to
	 * 0 on every start.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *      - ERR_OK if all went according to plan
	 *      - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	*/
	__declspec(dllimport) ErrCode setResetFrameCounterOnStart(TaskHandle t, bool do_reset);
	__declspec(dllimport) ErrCode getResetFrameCounterOnStart(TaskHandle t, bool* val);


	/**
	* @brief Get the precise time (in seconds) that a sweep will take.
	*
	* @param t Handle for the current task
	* @return Sweep time, as a double, in fractional seconds.
	*      If the task is not valid, or in the correct state,
	*      the return value is -1.
	*/
	__declspec(dllimport) double getPreciseTimePerFrame(TaskHandle t);


	/**
	 * @brief Add a band where transmission is disabled.
	 * @details Exclusion bands are used to prevent the AVMU from transmitting in specific
	 *          frequency ranges. This is generally used to "mask out" sensitive RF regions,
	 *          so things like GPS are not negatively affected by the AVMU.
	 *          The AVMU will still take data at points within the exclusion band, but
	 *          the RF Output will be disabled.
	 *          Multiple exclusion bands are logically ORed together. Basically, if
	 *          a frequency point falls within *any* exclusion band, it will result in the
	 *          RF output being disabled.
	 *          As such, repeated or overlapping exclusion bands are not invalid (though
	 *          they are somewhat pointless).
	 *          Note that you cannot add exclusion bands before connecting to an AVMU.
	 *
	 *
	 *          Note:
	 *           - Exclusion bands are not bounds-checked, so you can add exclusion bands
	 *             that do not intersect with the sweepable frequencies.
	 *           - `start_freq` and `stop_freq` must be positive, non-zero values, with
	 *             `start_freq` being smaller then `stop_freq`.
	 *
	 * @param start_freq Start frequency of the exclusion band region in Mhz
	 * @param stop_freq  Stop frequency of the exclusion band region in Mhz
	 *
	* @return Call status - Possible return values:
	*        - ERR_OK if all went according to plan
	*        - ERR_INVALID_PARAMETER if the parameters do not make sense.
	*        - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode addExclusionBand(TaskHandle t, double start_freq, double stop_freq);

	/**
	 * @brief Clear the set exclusion bands.
	 * @details Clear the internal list of exclusion bands from
	 *          within a task.
	* @return Call status - Possible return values:
	*        - ERR_OK if all went according to plan
	*        - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode clearExclusionBands(TaskHandle t);

	/**
	 * @brief Get the number of set exclusion bands.
	 * @details Fetch the number of exclusion bands in the task. This is
	 *          required for querying for individual exclusion bands,
	 *          via getExclusionBand(), or checking if there are any enabled
	 *          exclusion bands.
	 *
	 * @param idx        Pointer to integer into which the number of active exclusion
	 *            bands is written.
	* @return Call status - Possible return values:
	*        - ERR_OK if all went according to plan
	*        - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode getExclusionBandCount(TaskHandle t, int* idx);

	/**
	 * @brief Get a specific exclusion band value from the task.
	 * @details Given a index of 0 <= idx < getExclusionBandCount(), return
	 *          the corresponding exclusion band start/end frequency.
	 *
	 * @param idx        exclusion band index to query for.
	 * @param start_freq Pointer into which the start frequency of
	 *                   exclusion band idx will be written. In mhz.
	 * @param stop_freq  Pointer into which the stop frequency of
	 *                   exclusion band idx will be written. In mhz.
	* @return Call status - Possible return values:
	*        - ERR_OK if all went according to plan
	*        - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	*        - ERR_INDEX_OUT_OF_BOUNDS if the specified index is not valid.
	*                                  Note that when no exclusion bands are
	*                                  specified, ALL possible values for idx
	*                                  are therefore invalid.
	 */
	__declspec(dllimport) ErrCode getExclusionBand(TaskHandle t, int idx, double* start_freq, double* stop_freq);


#endif



	/** \addtogroup AttenuationSettings
	 *  @brief Attenuation options for the attenuation parameter.
	 *
	 *  @{
	 */

	/**
	 * Attenuation value type. Treat this as an opaque type.
	 */
	typedef int Attenuation;
	__declspec(dllimport) Attenuation ATTEN_UNDEFINED;  //!< Attenuation value not set
	__declspec(dllimport) Attenuation ATTEN_0;          //!< Attenuation value of 0 dB
	__declspec(dllimport) Attenuation ATTEN_1;          //!< Attenuation value of 1 dB
	__declspec(dllimport) Attenuation ATTEN_2;          //!< Attenuation value of 2 dB
	__declspec(dllimport) Attenuation ATTEN_3;          //!< Attenuation value of 3 dB
	__declspec(dllimport) Attenuation ATTEN_4;          //!< Attenuation value of 4 dB
	__declspec(dllimport) Attenuation ATTEN_5;          //!< Attenuation value of 5 dB
	__declspec(dllimport) Attenuation ATTEN_6;          //!< Attenuation value of 6 dB
	__declspec(dllimport) Attenuation ATTEN_7;          //!< Attenuation value of 7 dB
	__declspec(dllimport) Attenuation ATTEN_8;          //!< Attenuation value of 8 dB
	__declspec(dllimport) Attenuation ATTEN_9;          //!< Attenuation value of 9 dB
	__declspec(dllimport) Attenuation ATTEN_10;         //!< Attenuation value of 10 dB
	__declspec(dllimport) Attenuation ATTEN_11;         //!< Attenuation value of 11 dB
	__declspec(dllimport) Attenuation ATTEN_12;         //!< Attenuation value of 12 dB
	__declspec(dllimport) Attenuation ATTEN_13;         //!< Attenuation value of 13 dB
	__declspec(dllimport) Attenuation ATTEN_14;         //!< Attenuation value of 14 dB
	__declspec(dllimport) Attenuation ATTEN_15;         //!< Attenuation value of 15 dB
	__declspec(dllimport) Attenuation ATTEN_16;         //!< Attenuation value of 16 dB
	__declspec(dllimport) Attenuation ATTEN_17;         //!< Attenuation value of 17 dB
	__declspec(dllimport) Attenuation ATTEN_18;         //!< Attenuation value of 18 dB
	__declspec(dllimport) Attenuation ATTEN_19;         //!< Attenuation value of 19 dB
	__declspec(dllimport) Attenuation ATTEN_20;         //!< Attenuation value of 20 dB
	__declspec(dllimport) Attenuation ATTEN_21;         //!< Attenuation value of 21 dB
	__declspec(dllimport) Attenuation ATTEN_22;         //!< Attenuation value of 22 dB
	__declspec(dllimport) Attenuation ATTEN_23;         //!< Attenuation value of 23 dB
	__declspec(dllimport) Attenuation ATTEN_24;         //!< Attenuation value of 24 dB
	__declspec(dllimport) Attenuation ATTEN_25;         //!< Attenuation value of 25 dB
	__declspec(dllimport) Attenuation ATTEN_26;         //!< Attenuation value of 26 dB
	__declspec(dllimport) Attenuation ATTEN_27;         //!< Attenuation value of 27 dB
	__declspec(dllimport) Attenuation ATTEN_28;         //!< Attenuation value of 28 dB
	__declspec(dllimport) Attenuation ATTEN_29;         //!< Attenuation value of 29 dB
	__declspec(dllimport) Attenuation ATTEN_30;         //!< Attenuation value of 30 dB
	__declspec(dllimport) Attenuation ATTEN_31;         //!< Attenuation value of 31 dB
	/** @}*/


	typedef int RFPath;
	// These are the paths available on the switchboard used by the VNA product
	__declspec(dllimport) RFPath PATH_T1R1; //!< Out port T1, in port T1
	__declspec(dllimport) RFPath PATH_T1R2; //!< Out port T1, in port T2
	__declspec(dllimport) RFPath PATH_T2R1; //!< Out port T2, in port T1
	__declspec(dllimport) RFPath PATH_T2R2; //!< Out port T2, in port T2
	__declspec(dllimport) RFPath PATH_REF;  //!< Reference path

	/** \addtogroup SParameterSelector
	 *  @brief Available S-parameter measurements.
	 *
	 *
	 *  @{
	 */
	/**
	 * S-parameter path selector type. Treat this as an opaque type.
	 */
	typedef int SParameter;
	__declspec(dllimport) SParameter PARAM_S11;  //!< S11 Parameter
	__declspec(dllimport) SParameter PARAM_S21;  //!< S21 Parameter
	__declspec(dllimport) SParameter PARAM_S12;  //!< S12 Parameter
	__declspec(dllimport) SParameter PARAM_S22;  //!< S22 Parameter
	/** @}*/

	/** \addtogroup CalibrationStep
	 *  @brief Available calibration steps.
	 *
	 *  @{
	 */
	/**
	 * Calibration mode type. Treat this as an opaque type.
	 */
	typedef int CalibrationStep;
	__declspec(dllimport) CalibrationStep STEP_P1_OPEN;   //!< Calibration step for measuring a open on port 1
	__declspec(dllimport) CalibrationStep STEP_P1_SHORT;  //!< Calibration step for measuring a short on port 1
	__declspec(dllimport) CalibrationStep STEP_P1_LOAD;   //!< Calibration step for measuring a load on port 1
	__declspec(dllimport) CalibrationStep STEP_P2_OPEN;   //!< Calibration step for measuring a open on port 2
	__declspec(dllimport) CalibrationStep STEP_P2_SHORT;  //!< Calibration step for measuring a short on port 2
	__declspec(dllimport) CalibrationStep STEP_P2_LOAD;   //!< Calibration step for measuring a load on port 2
	__declspec(dllimport) CalibrationStep STEP_THRU;      //!< Calibration step for measuring a through from port 1 - port 2
	/** @}*/

	/**
	 * Container struct for passing IQ data sets around.
	 * The `I` and `Q` members are pointers to caller-allocated
	 * arrays of the requisite type (double, in this case).
	 */

	typedef struct
	{
		/** In-phase component value array */
		double* I;
		/** Quadrature component value array */
		double* Q;
	} ComplexData;

	/**
	 * @brief Attempts to program the VNA using the settings stored in the Task object. If it
	 *        succeeds the Task enters the TASK_STARTED state.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *
	 * @return Call status - Possible return values:
	 *          - ERR_OK if all went according to plan
	 *          - ERR_SOCKET if there was a problem sending a message
	 *          - ERR_NO_RESPONSE if the unit did not respond to commands
	 *          - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	 *          - ERR_MISSING_HOP if the hop rate has not yet been specified
	 *          - ERR_MISSING_ATTEN if the attenuation has not yet been specified
	 *          - ERR_MISSING_FREQS if the frequencies have not yet been specified
	 *          - ERR_PROG_OVERFLOW if the size of the program is too large for the hardware's memory
	 *                    (this can happen if the VNA is asked to sample too many frequency points)
	 */
	__declspec(dllimport) ErrCode start(TaskHandle t);

	/**
	 * @brief Puts the Task object into the TASK_STOPPED state.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *           - ERR_OK if all went according to plan
	 *           - ERR_WRONG_STATE if the Task is not in the TASK_STARTED state
	 */
	__declspec(dllimport) ErrCode stop(TaskHandle t);


	/**
	 * @brief Sets the IPv4 address on which to communicate with the unit.
	 *        The ipv4 parameter is copied into the Task's memory.
	 *        On success the Task's state will be TASK_UNINITIALIZED.
	 *        Example: setIPAddress(t, "192.168.1.197");
	 *
	 * @param t Handle for the current task
	 * @param ipv4 ASCII String IP representation, e.g. "192.168.1.207", etc...
	 *
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - ERR_MISSING_IP if the pointer is null
	 *       - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED or TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode setIPAddress(TaskHandle t, const char* ipv4);

	/**
	 * @brief Sets the port on which to communicate with the unit.
	 *        In general, ports >= 1024 should be used. On success
	 *        the Task's state will be TASK_UNINITIALIZED.
	 *
	 * @param t Handle for the current task
	 * @param port integer port number
	 *
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED or TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode setIPPort(TaskHandle t, const int port);

	//
	//
	/**
	 * @brief Sets the default time to wait, in milliseconds, for a unit to
	 *        reply to a command before giving up and returning an ERR_NO_RESPONSE
	 *        condition. For the measurement functions, this is the amount
	 *        of time to wait beyond the expected sweep time. When a Task is
	 *        created, the timeout value defaults to 150.
	 *
	 *   TODO: VALIDATE THIS - What happens if passed 0?
	 *
	 * @param t Handle for the current task
	 * @param timeout timeout in milliseconds
	 *
	 * @return Always returns ERR_OK.
	 */
	__declspec(dllimport) ErrCode setTimeout(TaskHandle t, const unsigned int timeout);

	/**
	 * @brief Set the frequency hopping rate. See the values defined in the "HopRate" type above.
	 *
	 * @param t Handle for the current task
	 * @param rate HopRate as member of HopRate type.
	 *
	 * @return Call status - Possible return values:
	 *      - ERR_OK if all went according to plan
	 *      - ERR_BAD_HOP if there was something wrong with the hop rate parameter
	 *      - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED or TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode setHopRate(TaskHandle t, const HopRate rate);

	/**
	 * @brief Set the attenuation amount. See the values defined above.
	 *
	 * @param t Handle for the current task
	 * @param atten One of the `Attenuation` types defined in the DLL
	 *
	 * @return Call status - Possible return values:
	 *        - ERR_OK if all went according to plan
	 *        - ERR_BAD_ATTEN if there was something wrong with the attenuation parameter
	 *        - ERR_WRONG_STATE if the Task is not in the TASK_UNINITIALIZED or TASK_STOPPED state
	 */
	__declspec(dllimport) ErrCode setAttenuation(TaskHandle t, const Attenuation atten);

	//
	/**
	 * @brief Get the attenuation associated with this Task object. If no attenuation value has yet been set,  this function returns ATTEN_UNDEFINED.
	 * @details [long description]
	 *
	 * @param t Handle for the current task
	 * @return Attenuation for Task `t`.
	 */
	__declspec(dllimport) Attenuation getAttenuation(TaskHandle t);

	/**
	 * @brief Measures the paths through the VNA, without applying calibration.
	 *       The ComplexData parameters are objects that contain pointers to data arrays that
	 *       the caller has allocated. This function copies the returned data into those arrays,
	 *       so they must have a minimum length of getNumberOfFrequencies().
	 *       Note that this function blocks while the measurement is being performed. Use the
	 *       interruptMeasurement() function to prematurely halt a slow measurement. The automatic
	 *       timeout value is the length of the measurement plus getTimeout().
	 *       Note that it is safe to supply null pointers.
	 *
	 * @param t Handle for the current task
	 * @param T1R1 Transmit port 1, receive port 1 reading.
	 * @param T1R2 Transmit port 1, receive port 2 reading.
	 * @param T2R1 Transmit port 2, receive port 1 reading.
	 * @param T2R2 Transmit port 2, receive port 2 reading.
	 * @param Ref Reference reading
	 * @return Call status - Possible return values:
	 *        - ERR_OK if all went according to plan
	 *        - ERR_SOCKET if there was a problem sending a message
	 *        - ERR_NO_RESPONSE if the unit did not respond to commands
	 *        - ERR_WRONG_STATE if the Task is not in the TASK_STARTED state
	 *        - ERR_BAD_PATH if there is something wrong with the paths parameter
	 *        - ERR_BYTES if the wrong number of bytes were received
	 *        - ERR_INTERRUPTED if the measurement was interrupted
	 */
	__declspec(dllimport) ErrCode measureUncalibrated(TaskHandle t,
	                                       ComplexData T1R1, ComplexData T1R2,
	                                       ComplexData T2R1, ComplexData T2R2,
	                                       ComplexData Ref);

	/**
	 * @brief Measures the S-parameter(s) of your choice, applying the current calibration.
	 *         Only paths specified by the 'paths' parameter get data copied into the output
	 *         ComplexData structures. To select more than one path, bitwise-OR the constants
	 *         together, e.g. `PARAM_S11 | PARAM_S22`
	 *         Like the other measurement functions, the ComplexData structures contain pointers
	 *         to memory that you the caller have allocated.
	 *         Note that this function blocks while the measurement is being performed. Use the
	 *         interruptMeasurement() function to prematurely halt a slow measurement.
	 *         You must pass buffers for all parameters, even if you don't want to measure them.
	 *         Possible return values:
	 *
	 * @param t Handle for the current task
	 * @param S11 User-Allocated \ref ComplexData() instance.
	 * @param S21 User-Allocated \ref ComplexData() instance.
	 * @param S12 User-Allocated \ref ComplexData() instance.
	 * @param S22 User-Allocated \ref ComplexData() instance.
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - ERR_SOCKET if there was a problem sending a message
	 *       - ERR_NO_RESPONSE if the unit did not respond to commands
	 *       - ERR_WRONG_STATE if the Task is not in the TASK_STARTED state
	 *       - ERR_BAD_PATH if there is something wrong with the paths parameter
	 *       - ERR_BAD_CAL if the calibration is missing (i.e. `isCalibrationComplete() == false`)
	 *       - ERR_BYTES if the wrong number of bytes were received
	 *       - ERR_INTERRUPTED if the measurement was interrupted
	 */
	__declspec(dllimport) ErrCode measure2PortCalibrated(TaskHandle t,
	        ComplexData S11, ComplexData S21,
	        ComplexData S12, ComplexData S22);

	/**
	 * @brief Measures the paths necessary to get data for the requested calibration step.
	 *         Note that this function blocks while the measurement is being performed. Use the
	 *         interruptMeasurement() function to prematurely halt a slow measurement.
	 *         Possible return values:
	 *
	 * @param t Handle for the current task
	 * @param step Which step of the calibration process you want to run. One of
	 *             \ref CalibrationStep options.
	 *
	 * @return Call status - Possible return values:
	 *       - ERR_OK if all went according to plan
	 *       - ERR_SOCKET if there was a problem sending a message
	 *       - ERR_NO_RESPONSE if the unit did not respond to commands
	 *       - ERR_WRONG_STATE if the Task is not in the TASK_STARTED state
	 *       - ERR_BAD_CAL if the current calibration settings do not match the current
	 *         sweep settings (clear the calibration first before recalibrating)
	 *       - ERR_BYTES if the wrong number of bytes were received
	 *       - ERR_INTERRUPTED if the measurement was interrupted
	 */
	__declspec(dllimport) ErrCode measureCalibrationStep(TaskHandle t, CalibrationStep step);

// These functions let you know the status of the internal raw data arrays
// for each calibration step
	/** Return whether internal cal array for the Port-1 open measurement is present  */
	__declspec(dllimport) bool haveCalP1Open(TaskHandle t);
	/** Return whether internal cal array for the Port-1 shorted measurement is present  */
	__declspec(dllimport) bool haveCalP1Short(TaskHandle t);
	/** Return whether internal cal array for the Port-1 load measurement is present  */
	__declspec(dllimport) bool haveCalP1Load(TaskHandle t);
	/** Return whether internal cal array for the Port-2 open measurement is present  */
	__declspec(dllimport) bool haveCalP2Open(TaskHandle t);
	/** Return whether internal cal array for the Port-2 shorted measurement is present  */
	__declspec(dllimport) bool haveCalP2Short(TaskHandle t);
	/** Return whether internal cal array for the Port-2 load measurement is present  */
	__declspec(dllimport) bool haveCalP2Load(TaskHandle t);
	/** Return whether internal cal array for the through-cal measurement is present  */
	__declspec(dllimport) bool haveCalThru(TaskHandle t);


	/**
	 * @brief Delete any calibration data stored in the Task `t`.
	 *
	 * @param t Handle for the current task
	 * @return Always returns `ERR_OK`
	 */
	__declspec(dllimport) ErrCode clearCalibration(TaskHandle t);

	/**
	 * @brief Query if calibration parameters are present in the task.
	 *
	 * @param t Handle for the current task
	 * @return true if the task has cal parameters, false otherwise.
	 */
	__declspec(dllimport) bool isCalibrationComplete(TaskHandle t);

	/**
	 * @brief Get the number of frequencies in the calibration data
	 *
	 * @param t Handle for the current task
	 * @return number of frequencies in calibration data.
	 */
	__declspec(dllimport) size_t getCalibrationNumberOfFrequencies(TaskHandle t);

	/**
	 * @brief Get a pointer to the list of frequencies used in the calibration data.
	 *        This pointer becomes invalid after clearCalibration() is called.
	 *        When no calibration data is loaded, this returns 0.
	 *        Calibration data must be loaded via a measureCalibrationStep() call.
	 *
	 * @param t Handle for the current task
	 * @return Pointer to array of double containing calibration frequencies.
	 *         array size can be determined by calling `getCalibrationNumberOfFrequencies()`
	 */
	__declspec(dllimport) const double* getCalibrationFrequencies(TaskHandle t);


	/**
	 * @brief Copies out the calibration coefficients to caller-allocated arrays. Note that
	 *          to fully contain a calibration the caller must also get the frequency list
	 *          and number of frequencies. It is the caller's responsibility to ensure the
	 *          arrays have enough memory allocated to hold all of the data. It is
	 *          recommended to use the getCalibrationNumberOfFrequencies() function to get the
	 *          length because the number of calibration frequencies does not have to match
	 *          the number of sweep frequencies.
	 *
	 *       The calibration terms are for a full, 12-term model.
	 *
	 * @param t Handle for the current task
	 * @param e00 EDF Calibration term.
	 * @param e11 ESF Calibration term.
	 * @param e10e01 ERF Calibration term.
	 * @param e30 EXF Calibration term.
	 * @param e22 ELF Calibration term.
	 * @param e10e32 ETF Calibration term.
	 * @param ep33 EDR Calibration term.
	 * @param ep22 ESR Calibration term.
	 * @param ep23ep32 ERR Calibration term.
	 * @param ep03 EXR Calibration term.
	 * @param ep11 ELR Calibration term.
	 * @param ep23ep01 ETR Calibration term.
	 *
	 * @return Call status - Possible return values:
	 *         - ERR_OK if all went according to plan
	 *         - ERR_BAD_CAL if isCalibrationComplete() returns false
	 */
	__declspec(dllimport) ErrCode exportCalibration(TaskHandle t,
	                                     ComplexData e00,		/* EDF */
	                                     ComplexData e11,		/* ESF */
	                                     ComplexData e10e01,		/* ERF */
	                                     ComplexData e30,		/* EXF */
	                                     ComplexData e22,		/* ELF */
	                                     ComplexData e10e32,		/* ETF */
	                                     ComplexData ep33,		/* EDR */
	                                     ComplexData ep22,		/* ESR */
	                                     ComplexData ep23ep32,	/* ERR */
	                                     ComplexData ep03,		/* EXR */
	                                     ComplexData ep11,		/* ELR */
	                                     ComplexData ep23ep01	/* ETR */);

	/**
	 * @brief Imports calibration coefficients from caller-allocated arrays. Note that these
	 *        frequencies do not have to be exactly generateable by the hardware. At import
	 *        an interpolated calibration is generated that matches the current sweep settings.
	 *        Altering sweep settings automatically generates a new interpolated calibration
	 *        from the original imported data provided here. Data is copied out of these
	 *        arrays into the Tasks's memory.
	 *
	 *       The calibration terms are for a full, 12-term model.
	 *
	 * @param t Handle for the current task
	 * @param freqs Double[] of frequencies for the calibration data.
	 * @param N Size of `freqs` value
	 * @param e00 EDF calibration term.
	 * @param e11 ESF calibration term.
	 * @param e10e01 ERF calibration term.
	 * @param e30 EXF calibration term.
	 * @param e22 ELF calibration term.
	 * @param e10e32 ETF calibration term.
	 * @param ep33 EDR calibration term.
	 * @param ep22 ESR calibration term.
	 * @param ep23ep32 ERR calibration term.
	 * @param ep03 EXR calibration term.
	 * @param ep11 ELR calibration term.
	 * @param ep23ep01 ETR calibration term.
	 *
	 * @return Call status - Possible return values:
	 *         - ERR_OK if all went according to plan
	 *         - ERR_BAD_CAL if any of the array pointers are null
	 *         - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED or TASK_STARTED state
	 */
	__declspec(dllimport) ErrCode importCalibration(TaskHandle t,
	                                     const double* freqs,
	                                     const unsigned int N,
	                                     const ComplexData e00,		/* EDF */
	                                     const ComplexData e11,		/* ESF */
	                                     const ComplexData e10e01,	/* ERF */
	                                     const ComplexData e30,		/* EXF */
	                                     const ComplexData e22,		/* ELF */
	                                     const ComplexData e10e32,	/* ETF */
	                                     const ComplexData ep33,		/* EDR */
	                                     const ComplexData ep22,		/* ESR */
	                                     const ComplexData ep23ep32,	/* ERR */
	                                     const ComplexData ep03,		/* EXR */
	                                     const ComplexData ep11,		/* ELR */
	                                     const ComplexData ep23ep01	/* ETR */);

	/**
	 * @brief Determine of the VNA has a factory calibration stored in it's
	 *        onboard EEPROM.
	 *
	 * @param t Handle for the current task
	 * @return True if the EEPROM has a factory calibration, False if not.
	 */
	__declspec(dllimport) bool hasFactoryCalibration(TaskHandle t);

	/**
	 * @brief Load the factory calibration from the VNA into the current task.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *          - ERR_BAD_CAL if the unit doesn't have a factory calibration
	 *          - ERR_WRONG_STATE if the task is not in the TASK_STOPPED or TASK_STARTED state
	 */
	__declspec(dllimport) ErrCode importFactoryCalibration(TaskHandle t);

	/**
	 * @brief  Set phase correction factors for the open used during calibration.
	 *         Each time calibration parameters are computed from raw data, these phases
	 *         are added to the phase of the 'open' data. The operation is not cumulative,
	 *         meaning if you first set a value of 6, and then 7, the final corrected phase
	 *         is +7, not +13.
	 *         Because there is one phase for each frequency point, this call only succeeds
	 *         when the task is in the TASK_STOPPED or TASK_STARTED state.
	 *         The data you provide here is internally copied, so the passed pointer need
	 *         not remain valid after the call. Null may be passed as a shortcut to setting
	 *         the offset to zero for all frequencies.
	 *
	 * @param t Handle for the current task
	 * @param phaseCorrections Phase correction value in radians.
	 *
	 * @return Call status - Possible return values:
	 *          - ERR_OK
	 *          - ERR_BAD_CAL if `!(haveCalP1Open() || haveCalP2Open())`
	 *          - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED or TASK_STARTED state
	 */
	//__declspec(dllimport) ErrCode setOpenPhaseCorrection(TaskHandle t, const double* const phaseCorrections);



// <<<<<< CPP WRAP START

	#ifdef __cplusplus
		}  // end extern
	#endif

// CPP WRAP END >>>>>>>>




/** @}*/

#endif
#endif

		