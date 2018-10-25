


/** \addtogroup Avmu-C-API
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
 *  the assumption is that a different AVMU unit is going to be targeted.
 *  Hardware details can vary from unit to unit and so those details must be
 *  re-downloaded prior to programming the new unit.
 *  NOTE: any calibration data is marked invalid when the state transitions
 *  to uninitialized. If you would like to use the calibration on a different
 *  unit (or save it for later), see the exportCalibration() function.
 *
 */
// AVMUDLL_EXPORTS should only be defined when building the DLL.
// Do not define it when linking to this DLL




/** \addtogroup Avmu-C-API
 *  @{
 */

	
// Common include-guards

	// <<<<<< SPLICE_POINT (do not change this line!) >>>>>>

	


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
	 ErrCode ERR_OK;                                   //!< Return "error" code indicating no error occured.
	 ErrCode ERR_BAD_ATTEN;                            //!< Error code indicating the specified attenuation value was not valid.
	 ErrCode ERR_BAD_CAL;                              //!< Error code indicating the current calibration is invalid.
	 ErrCode ERR_BAD_HANDLE;                           //!< Error code indicating the current handle passed to a DLL function was not valid.
	 ErrCode ERR_BAD_HOP;                              //!< Error code indicating the specified hop-rate value was not valid.
	 ErrCode ERR_BAD_PATH;                             //!< Error code indicating the specified path is not allowed, or was invalid.
	 ErrCode ERR_BAD_PROM;                             //!< Error code indicating that the AVMU PROM was not in a known format.  Please contact support if this is a reoccuring issue
	 ErrCode ERR_BYTES;                                //!< Error code indicating the DLL has received an incorrect number of bytes from the AVMU. Possibly indicative of a network issue.
	 ErrCode ERR_EMPTY_PROM;                           //!< Error code indicating the remote device's PROM appears to be empty. Power cycle the AVMU, and if the problem persists, contact Akela.
	 ErrCode ERR_FEATURE_NOT_PRESENT;                  //!< You are trying to configure a hardware feature not present in the connected AVMU.
	 ErrCode ERR_FREQ_OUT_OF_BOUNDS;                   //!< Error code indicating one of the specified frequency bounds was beyong the hardware's available range.
	 ErrCode ERR_INTERRUPTED;                          //!< Error code indicating that the measurement was asynchronously interrupted from another thread.
	 ErrCode ERR_MISSING_FREQS;                        //!< Error code indicating you have not yet specified the frequency endpoints for the remote device before connecting.
	 ErrCode ERR_MISSING_HOP;                          //!< Error code indicating you have not yet specified the hop-rate for the remote device before connecting.
	 ErrCode ERR_MISSING_IP;                           //!< Error code indicating you have not yet specified the IP of the remote device before connecting.
	 ErrCode ERR_BAD_IP_PORT;                          //!< The UDP port you specified is not useable. You must use a port >= 1024 and < 65535
	 ErrCode ERR_MISSING_PORT;                         //!< Error code indicating you have not yet specified the port for the remote device before connecting.
	 ErrCode ERR_NO_PATHS_MEASURED;                    //!< Error code indicating there are no paths to measure, and the hardware has nothing to do.
	 ErrCode ERR_NO_RESPONSE;                          //!< Error code indicating the remote instrument failed to respond to commands within the current timeout period.
	 ErrCode ERR_PATH_ALREADY_MEASURED;                //!< Error code indicating you are adding a path to measure that you had already added.
	 ErrCode ERR_PROG_OVERFLOW;                        //!< Error code indicating the generated program to run on the remote device was larger then it can handle.
	 ErrCode ERR_SOCKET;                               //!< Error code indicating an unknown socket error occured.
	 ErrCode ERR_TOO_MANY_POINTS;                      //!< Error code indicating you are trying to take more data points then the hardware is capable of.
	 ErrCode ERR_UNKNOWN_FEATURE;                      //!< Error code indicating the AVMU's prom indicates it has a hardware feature that this
	                                                             //!< version of the DLL doesn't know about. Either indicates you need to update, or the prom is corrupted.
	 ErrCode ERR_WRONG_PROGRAM_TYPE;                   //!< Error code indicating you are in sync mode and are trying to call an async startup function.
	 ErrCode ERR_WRONG_STATE;                          //!< Error code indicating the hardware is not in the correct state for the function you are trying to call.
	 ErrCode ERR_MISSING_ATTEN;                        //!< The switchboard config requires an attenuation value to be specified, and it has not.
	 ErrCode ERR_NO_ATTEN_PRESENT;                     //!< You are trying to specify an attenuation value on hardware without an attenuator.
	 ErrCode ERR_TASK_ARRAY_INVALID;                   //!< The passed batch-task array appears to not be valid.
	 ErrCode ERR_PATH_HAS_NO_DATA;                     //!< No data was acquired for the specified path. Either you didn't add the path, didn't call measure(), or something else is wrong.
	 ErrCode ERR_INDEX_OUT_OF_BOUNDS;                  //!< the sweep index/exclusion band you are trying to extract is outside the bounds of valid values.
	 ErrCode ERR_INVALID_PARAMETER;                    //!< One of the specified parameters is not valid. If you are specifying sweep frequency, check your frequency bands.
	 ErrCode ERR_PROM_INVALID_FEATURE_CONFIGURATION;   //!< The AVMU's prom contains feature flags that are incompatible. Please contact support


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

	 HopRate HOP_UNDEFINED;  //!< Hop rate not set yet
		 HopRate HOP_90K;  //!< This rate is currently unsupported but may be enabled in the future 90K Pts/second
	 HopRate HOP_45K;  //!< Hop rate of 45K points/second
	 HopRate HOP_30K;  //!< Hop rate of 30K points/second
	 HopRate HOP_15K;  //!< Hop rate of 15K points/second
	 HopRate HOP_7K;   //!< Hop rate of 7K points/second
	 HopRate HOP_3K;   //!< Hop rate of 3K points/second
	 HopRate HOP_2K;   //!< Hop rate of 2K points/second
	 HopRate HOP_1K;   //!< Hop rate of 1K points/second
	 HopRate HOP_550;  //!< Hop rate of 550 points/second
	 HopRate HOP_312;  //!< Hop rate of 312 points/second
	 HopRate HOP_156;  //!< Hop rate of 156 points/second
	 HopRate HOP_78;   //!< Hop rate of 78 points/second
	 HopRate HOP_39;   //!< Hop rate of 39 points/second
	 HopRate HOP_20;   //!< Hop rate of 20 points/second
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
	 TaskState TASK_UNINITIALIZED; //!< Task state of uninitialized
	 TaskState TASK_STOPPED;       //!< Task state of stopped
	 TaskState TASK_STARTED;       //!< Task state of started
	 TaskState TASK_RUNNING;       //!< Task state of running

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

	 ProgramType PROG_ASYNC;  //!< Asynchronous acquisition mode
	 ProgramType PROG_SYNC;   //!< Synchronous acquisition mode


	/**
	 * Switchboard type.
	 */
	typedef int SwitchboardType;
	 SwitchboardType SWITCHBOARD_SIMPLE_4_PORT_SWITCH;
	 SwitchboardType SWITCHBOARD_TDD_4_PORT_SWITCH;
	 SwitchboardType SWITCHBOARD_NO_SWITCH_BOARD;
	 SwitchboardType SWITCHBOARD_SIMPLE_8_PORT_SWITCH;
	 SwitchboardType SWITCHBOARD_S_PARAMETER_SWITCH;

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
	 const char* versionString();

	/**
	 * @brief Creates a new Task object and returns a handle to it.
	 *        This handle is required by all of the other API
	 *        functions. The returned object is in the
	 *        TASK_UNINITIALIZED state.
	 * @return new task handle
	 */
	 TaskHandle createTask();

	/**
	 * @brief Deletes the Task object. If the caller does not do this, the handle memory will leak.
	 *
	 * @param t Task to delete
	 */
	 void deleteTask(TaskHandle t);

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
	 ErrCode initialize(TaskHandle t, progress_callback callback, void* user);

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
	 ErrCode start(TaskHandle t);

	/**
	 * @brief Puts the Task object into the TASK_STOPPED state.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *           - ERR_OK if all went according to plan
	 *           - ERR_WRONG_STATE if the Task is not in the TASK_STARTED state
	 */
	 ErrCode stop(TaskHandle t);


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
	 ErrCode setIPAddress(TaskHandle t, const char* ipv4);

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
	 ErrCode setIPPort(TaskHandle t, const int port);

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
	 ErrCode setTimeout(TaskHandle t, const unsigned int timeout);


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
	 ErrCode setFrequencies(TaskHandle t, const double* freqs, const unsigned int N);

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
	 ErrCode setHopRate(TaskHandle t, const HopRate rate);

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
	 ErrCode setShaftEncoderFeature(TaskHandle t, const bool enable, const bool reset_on_start);

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
	 ErrCode setSerialPortFeature(TaskHandle t, const bool enable, const unsigned int buffer_size);

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
	 ErrCode setMeasurementType(TaskHandle t, const ProgramType type);

	/**
	 * @brief Return the current measurement ProgramType type..
	 *
	 * @param t Handle for the current task
	 * @return One of the ProgramType types (PROG_ASYNC or PROG_SYNC)
	 */
	 ProgramType getMeasurementType(TaskHandle t);

	/**
	 * @brief Get the current state of the Task object. Returns one of the values defined above.
	 *
	 * @param t Handle for the current task
	 * @return A value from the TaskState state list
	 */
	 TaskState getState(TaskHandle t);

	//
	/**
	 * @brief Get the current time to wait for the unit to reply to commands. When a Task is first created, this will default to 100 ms.
	 *
	 * @param t Handle for the current task
	 * @return current timeout in milliseconds
	 */
	 unsigned int getTimeout(TaskHandle t);

	/**
	 * @brief Get the current AVMU IP address for the Task object.
	 *        When no IP has yet been set, this will return a NULL
	 *        char*.
	 *
	 * @param t Handle for the current task
	 * @return char* to string containing the AVMU IP address. NULL if not set.
	 */
	 const char* getIPAddress(TaskHandle t);

	/**
	 * @brief Get the current port for IP communications.
	 *        When uninitialized, this will default to 0.
	 *
	 * @param t Handle for the current task
	 * @return current port number
	 */
	 int getIPPort(TaskHandle t);

	//
	/**
	 * @brief Get the frequency hopping rate associated with this Task object.
	 *        If no rate has yet been set, this function returns HOP_UNDEFINED.
	 *
	 * @param t Handle for the current task
	 * @return HopRate for the Task `t` in question.
	 */
	 HopRate getHopRate(TaskHandle t);

	/**
	 * @brief Get the number of frequency points for the sweep configured for
	 *        Task `t`. If no frequencies have been set, this function returns 0.
	 *
	 * @param t Handle for the current task
	 * @return Number of frequency points in Task `t`.
	 */
	 unsigned int getNumberOfFrequencies(TaskHandle t);

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
	 ErrCode getFrequencies(TaskHandle t, double* freqs, int freqs_sz);

	/**
	 * @brief Get the hardware details for the unit associated with
	 *        Task `t`. If the Task has not yet been initialized, the
	 *        returned struct has all values set to 0.
	 *
	 * @param t Handle for the current task
	 * @return `HardwareDetails` containing the details of the connected
	 *                           hardware (if initialized), else zeroes.
	 */
	 HardwareDetails getHardwareDetails(TaskHandle t);

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
	 ErrCode utilNearestLegalFreq(TaskHandle t, double* freq);

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
	 ErrCode utilFixLinearSweepLimits(TaskHandle t, double* startFreq, double* endFreq, const unsigned int N);

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
	 ErrCode utilPingUnit(TaskHandle t, int tries);


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
	 ErrCode utilEnterLowPowerState(TaskHandle t);

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
	 ErrCode utilGenerateLinearSweep(TaskHandle t, const double startFreq, const double endFreq, const unsigned int N);



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
	 ErrCode interruptMeasurement(TaskHandle t);


	/**
	 * @brief Determines if the sweep timer is sent at the beginning of each frame.
	 * The sweep timer is a 32.768 MHz/256 clock which increments a 32 bit register.
	 *
	 * @param t Handle for the current task
	 * @return Call status - Possible return values:
	 *      - ERR_OK if all went according to plan
	 *      - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	*/
	 ErrCode setSendSweepTimer(TaskHandle t, bool send_timer);
	 ErrCode getSendSweepTimer(TaskHandle t, bool* val);


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
	 ErrCode setResetFrameCounterOnStart(TaskHandle t, bool do_reset);
	 ErrCode getResetFrameCounterOnStart(TaskHandle t, bool* val);


	/**
	* @brief Get the precise time (in seconds) that a sweep will take.
	*
	* @param t Handle for the current task
	* @return Sweep time, as a double, in fractional seconds.
	*      If the task is not valid, or in the correct state,
	*      the return value is -1.
	*/
	 double getPreciseTimePerFrame(TaskHandle t);


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
	 ErrCode addExclusionBand(TaskHandle t, double start_freq, double stop_freq);

	/**
	 * @brief Clear the set exclusion bands.
	 * @details Clear the internal list of exclusion bands from
	 *          within a task.
	* @return Call status - Possible return values:
	*        - ERR_OK if all went according to plan
	*        - ERR_WRONG_STATE if the Task is not in the TASK_STOPPED state
	 */
	 ErrCode clearExclusionBands(TaskHandle t);

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
	 ErrCode getExclusionBandCount(TaskHandle t, int* idx);

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
	 ErrCode getExclusionBand(TaskHandle t, int idx, double* start_freq, double* stop_freq);






	/** \addtogroup RFPathSelector
	*  @brief Available RF paths the hardware can support.
	*
	*  @{
	*/
	/**
	* RF path selector type. Treat this as an opaque type.
	*/
	typedef int TransmitPath;
	typedef int ReceivePath;


	// These are the paths available on the 4-port switchboard that can do TDD
	 TransmitPath AVMU_TX_PATH_0;
	 TransmitPath AVMU_TX_PATH_1;
	 TransmitPath AVMU_TX_PATH_2;
	 TransmitPath AVMU_TX_PATH_3;
	 TransmitPath AVMU_TX_PATH_4;
	 TransmitPath AVMU_TX_PATH_5;
	 TransmitPath AVMU_TX_PATH_6;
	 TransmitPath AVMU_TX_PATH_7;
	 TransmitPath AVMU_TX_PATH_NONE;

	 ReceivePath AVMU_RX_PATH_0;
	 ReceivePath AVMU_RX_PATH_1;
	 ReceivePath AVMU_RX_PATH_2;
	 ReceivePath AVMU_RX_PATH_3;
	 ReceivePath AVMU_RX_PATH_4;
	 ReceivePath AVMU_RX_PATH_5;
	 ReceivePath AVMU_RX_PATH_6;
	 ReceivePath AVMU_RX_PATH_7;
	 ReceivePath AVMU_RX_PATH_NONE;

	typedef int IfGain;

	 IfGain AVMU_GAIN_USE_DEFAULT;
	 IfGain AVMU_GAIN_0;
	 IfGain AVMU_GAIN_3;
	 IfGain AVMU_GAIN_6;
	 IfGain AVMU_GAIN_9;
	 IfGain AVMU_GAIN_12;
	 IfGain AVMU_GAIN_15;
	 IfGain AVMU_GAIN_18;
	 IfGain AVMU_GAIN_21;
	 IfGain AVMU_GAIN_24;
	 IfGain AVMU_GAIN_27;
	 IfGain AVMU_GAIN_30;
	 IfGain AVMU_GAIN_33;
	 IfGain AVMU_GAIN_36;
	 IfGain AVMU_GAIN_39;
	 IfGain AVMU_GAIN_42;
	 IfGain AVMU_GAIN_45;

	typedef int SyncPulseMode;

	 SyncPulseMode SYNC_IGNORE;
	 SyncPulseMode SYNC_GENERATE;
	 SyncPulseMode SYNC_RECEIVE;

	/** @}*/

	/**
	 * @brief [brief description]
	 * @details [long description]
	 *
	 * @param share_from [description]
	 * @return [description]
	 */
	 TaskHandle createSharedTask(TaskHandle share_from);

	/**
	 * @brief Begin async data collection.
	 *        This call emits the trigger message that will cause the remote hardware to
	 *        immediately begin acquiring frequency data continuously.
	 *
	 *        Note that once beginAsync() has been called, you MUST then call measure()
	 *        periodically so that the UDP recieve buffer will not overflow.
	 *
	 * @param t Handle for the current task
	 *
	 * @return TBD
	 */
	 ErrCode beginAsync(TaskHandle t);

	/**
	 * @brief This causes an immediate halt of the async sweep acquisition in the
	 *        remote hardware.
	 *
	 *        Any pending data in the UDP recieve buffer will be flushed, and the
	 *        hardware will be returned to the "started" state.
	 *
	 *        To resume async data collection after calling haltAsync(),
	 *        simply call beginAsync().
	 *
	 * @param t Handle for the current task
	 *
	 * @return TBD
	 */
	 ErrCode haltAsync(TaskHandle t);

	/**
	 * @brief Query feature flags to return whether the connected hardware supports
	 *        reading out a connected incremental encoder.
	 *
	 *
	 * @param t Handle for the current task
	 * @param present boolean reference into which the flag indicating the presence of
	 *                encoder read-out hardware. If true, the hardware can support the
	 *                tracking of 2 connected quadrature encoders.
	 *
	 * @return TBD
	 */
	 ErrCode isShaftEncoderPresent(TaskHandle t, bool* present);

	/**
	 * @brief Query feature flags to return whether the connected hardware supports
	 *        the local buffering and aggregation of a serial data source into the
	 *        acquired data stream.
	 *
	 *
	 * @param t Handle for the current task
	 * @param present boolean reference into which the flag indicating the presence of
	 *                serial RX hardware. True if the hardware is present.
	 *
	 * @return TBD
	 */
	 ErrCode isSerialPortPresent(TaskHandle t, bool* present);




	/**
	* @brief Add a path to measure.
	*        Adds a path to the list of active paths that will be
	*        measured when data is actually acquired.
	*
	* @param t Handle for the current task
	* @param path tx_path Transmitting port of the path to add. Note that
	*                     this can very well be TX_NONE, if your application is
	*                     using multiple AVMUs, and one of the other AVMUs is
	*                     the one actively transmitting.
	* @param path rx_path RX Path for the combo. This can be RX_NONE if there
	*                     is no need for the associated rx data. Note that RX_NON
	*                     will still return data (as the transmitter will still
	*                     need to do the associated frequency stepping), but the
	*                     return content will be only cross-board leakage within
	*                     the AVMU.
	*
	* @return ERR_OK, ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	*/
	 ErrCode addPathToMeasure(TaskHandle t, TransmitPath tx_path, ReceivePath rx_path);

	/**
	* @brief Clear list of paths being measured.
	*
	* @param t Handle for the current task
	*
	* @return ERR_OK, ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	*/
	 ErrCode clearMeasuredPaths(TaskHandle t);

	/**
	 * @brief Get the number of paths in the current measured path list.
	 *
	 * @param t Handle for the current task
	 * @param measured_path_count pointer to an int into which the number of
	 *                            measured paths will be written.
	 *
	 * @return ERR_OK, ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	 *                 ERR_WRONG_STATE if the task is either UNINITIALIZED or STOPPED.
	 */
	 ErrCode getMeasuredPathCount(TaskHandle t, int* measured_path_count);

	/**
	 * @brief Get the active ports for the path specified by index.
	 *        This is useful in conjunction with getMeasuredPathCount(). You call
	 *        getMeasuredPathCount() to get the number of paths, and then iteratively
	 *        call getPathAtIndex() for index 0 - index getMeasuredPathCount() - 1.
	 *
	 *
	 * @param t Handle for the current task
	 * @param path_idx index to extract the ports for. Must be >= 0 and < measuredPathCount.
 	 * @param tx_path Pointer into which the tx path is written.
	 * @param rx_path Pointer into which the rx path is written.
	 * @return ERR_OK, ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	 *                 ERR_WRONG_STATE if the task is either UNINITIALIZED or STOPPED.
	 *                 ERR_INDEX_OUT_OF_BOUNDS if the passed index is invalid for the current
	 *                 active paths..
	 */
	 ErrCode getPathAtIndex(TaskHandle t, const int path_idx, TransmitPath* tx_path, ReceivePath* rx_path);

	/**
	* @brief Take a measurement.
	 *        In PROG_SYNC mode, this triggers a measurement, and blocks until it's response has
	 *        been fully received and decoded.
	 *
	 *        If the TaskHandle t is in async mode (setMeasurementType called with PROG_ASYNC)
	 *        this simply serves to consume any UDP messages generated by the hardware. Note that
	 *        since the hardware asynchronously emits data continuously, you therefore
	 *        *must* call this periodically, or you risk overrunning the socket receive buffer.
	 *        Typically, overrunning the buffer will  result in a ERR_BYTES return code, but
	 *        it's theoretically possible to have an entire sweep be dropped (either if it
	 *        fits in a single packet, or if all the packets for the sweep get dropped).
	 *        In this case, the only indicator of data loss will be a non-monotonic sweep
	 *        number in the returned data.
	 *        In general, it's probably ideal to just continualy call this.
	 *
	 *        In both cases, measure places the acquired data in the RX queue, ready
	 *        to be extracted by calling extractSweepData().
	*
	* @param t Handle for the current task
	*
	 * @return ERR_OK,
	 *         ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	 *         ERR_WRONG_STATE if the task is in PROG_SYNC mode, and the task
	 *                         state is not TASK_STARTED.
	 *         ERR_WRONG_STATE if the task is in PROG_ASYNC mode, and the task
	 *                         state is not TASK_RUNNING.
	 *         ERR_NO_PATHS_MEASURED if there are no paths added to measure.
	 *         ERR_BYTES if the received data is corrupted in some manner.
	 *
	 * Rare ERR_BYTES, particularly when not on a dedicated subnet are
	 * not entirely unknown, but they shouldn't happen frequently.
	 *
	 * If you encounter large numbers of ERR_BYTES returns, there can be a number of
	 * causes. TCP Checksum offloading has been known to cause this, as could
	 * not calling measure() frequently enough. Lastly, check the intervening network
	 * hardware. You might have a failing switch/hub.
	 * Note that the AVMU hardware is particularly intolerant of network hubs,
	 * as it's UDP transport does not support data retransmits. Any collisions
	 * will result in a corrupted sweep (but really, it's 2018+, why are you
	 * running a network hub?).
	 *
	*/
	 ErrCode measure(TaskHandle t);


	/**
	* @brief Copy the sweep data acquired by measure() for RFPath path into the user-
	*        provided data-structure data.
	*
	* @param t Handle for the current task
	* @param path tx_path Transmitting port of the path to extract.
	* @param path rx_path RX Path for the combo to extract.
	* @param data SweepDataStruct into which the acquired data is written. The size of the
	*             various member arrays must be can be determined by calling the various
	*             API functions getNumberOfFrequencies(), getnumberOfEnabledReceivers(),
	*             and the buffer size passed to setSerialPortFeature().
	*
	 * @return ERR_OK,
	 *         ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	 *         ERR_BAD_PATH if the path you passed to extract was not measured.
	 *         ERR_BYTES if the received data is corrupted in some manner.
	 *         ERR_PATH_HAS_NO_DATA  - Generally indicates an internal error. Please
	 *                                 contact Akela so we can fix whatever is going on.
	*/
	 ErrCode extractSweepData(TaskHandle t, SweepDataStruct* data, TransmitPath tx_path, ReceivePath rx_path);

	/*
	* @brief Given an array of task-pointers, check to be certain the settings of each task
	*        make sense for a coordinated acquisition.
	*
	 * @param t Array of task handles for which the configuration will be validated.
	 * @param handle_count the number of handles in the t[] array.
	*
	 * @return [description]
	*/
	 ErrCode validateArrayTasks(TaskHandle t[], int handle_count);


	/*
	* @brief Broadcast a "begin" command to all avmus on the local network. This will start the
	*        sweep of ever avmu on the network at the current position of it's internal PC, and
	*        therefore depends on the avmus having been preconfigured to the proper start addresses
	*        using beginAsync().
	*
	* @param t Handle for a task with an open UDP socket on the current LAN.
	*
	 * @return ERR_OK, ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	 *                 ERR_WRONG_STATE if any of the the tasks are not in the TASK_RUNNING state.
	 *                 ERR_TASK_ARRAY_INVALID if the passed array is empty (handle_count == 0)
	*
	*/
	 ErrCode broadcastBeginCommand(TaskHandle t[], int handle_count);


	/**
	 * @brief Set the inter-unit synchronization pulse mode for a specified AVMU.
	 * @details The SyncPulseMode is used to allow coordinated acquisition between
	 *          multiple AVMUs. In coordinated operation, the master unit is set to
	 *          SYNC_GENERATE, and any slave units are set to SYNC_RECEIVE. This
	 *          causes the master to emit sweep start outputs, which are consumed
	 *          by the slave units.
	 *
	 *          Note that this requires specialized hardware support, and dedicated
	 *          syncronization wiring.
	 *
	 *          Additionally, to properly synchronize, all units must receive their
	 *          start command within 1 ms of each other, which is accomplished via
	 *          the broadcastBeginCommand() call. This also requires the
	 *          shared-communication-infrasturcture provided by the createSharedTask()
	 *          call. All AVMU tasks used in a coordinated acqusition must share
	 *          their internal communication object.
	 *
	 * @param t Array of task handles for which the configuration will be validated.
	 * @param sync_mode SYNC_IGNORE, SYNC_GENERATE or SYNC_RECEIVE
	 *
	 * @return ERR_OK, ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	 *                 ERR_WRONG_STATE if the task is either UNINITIALIZED or STOPPED.
	 */
	 ErrCode setSyncPulseMode(TaskHandle t, SyncPulseMode sync_mode);
	 ErrCode getSyncPulseMode(TaskHandle t, SyncPulseMode* sync_mode);

	/*
	* @brief Configure multiple receivers, if the hardware supports them
	*        Internal use only, at the moment. No released hardware has multiple receivers
	*        enabled.
	*/
	 ErrCode getnumberOfEnabledReceivers(TaskHandle t, int*  num_receivers_enabled);
	 ErrCode getEnabledReceivers(TaskHandle t,         char* enabled_receivers_mask);
	 ErrCode setEnabledReceivers(TaskHandle t,         char  enabled_receivers_mask);


	/**
	 * @brief Control intermediate IF gain.
	 * @details The AVMU has the facility for configurable  gain within the IF stage
	 *          of the RF pipeline.
	 *
	 * @param t Array of task handles for which the configuration will be validated.
	 * @param new_gain A value in the IfGain Enum (AVMU_GAIN_*)
	 *
	 * @return ERR_OK, ERR_BAD_HANDLE if t is not a valid TaskHandle instance.
	 *                 ERR_WRONG_STATE if the task is either UNINITIALIZED or STOPPED.
	 */
	 ErrCode setIfGain(TaskHandle t, IfGain new_gain);
	 ErrCode getIfGain(TaskHandle t, IfGain* current_gain);

	/**
	 * @brief TODO
	 *
	 * @param t [description]
	 * @param enable_12_db_pad [description]
	 *
	 * @return [description]
	 */
	 ErrCode setReceiver12dBPad(TaskHandle t, bool enable_12_db_pad);
	 ErrCode getReceiver12dBPad(TaskHandle t, bool* is_enabled_12_db_pad);


	/*
	* @brief Configure the TDD board settings.
	*        This is a horrible messy pile of magic values that get shoved out
	*        to the TDD board, and make it do ~things~.
	*
	* @param t Handle for a task with an open UDP socket on the current LAN.
	* @param tddEnabled boolean that determines if anything is done with the
	*                   TDD configuration values.
	* @param the_rest_of_the_registers More or less what they're named.
	*                                  Note that there is no bounds checking
	*                                  done on the various register values, so
	*                                  values out-of-scope for the registers
	*                                  will have unknown effects.
	*
	* @return TBD
	*
	*/
	 ErrCode configureTddSettings(TaskHandle t,
		bool tddBoardActive,
		bool tddEnabled,
		bool nullingEnabled,
		bool powerAmpState,
		bool slave,
		bool attenuatorEnabled,
		bool lnaEnabled,
		unsigned short attenuatorValue,
		unsigned int tx,
		unsigned int tx_to_rx1,
		unsigned int rx1,
		unsigned int rx1_to_rx2,
		unsigned int rx2,
		unsigned int rx2_to_tx);

	/*
	// configureTDDFeature
	bool tddEnabled;
	bool nullingEnabled;
	bool powerAmpState;
	bool slave;
	bool attenuatorEnabled;
	unsigned short attenuatorValue;
	bool lnaEnabled;

	int tdd_reg_0;

	unsigned int tx;
	unsigned int tx_to_rx1;
	unsigned int rx1;
	unsigned int rx1_to_rx2;
	unsigned int rx2;
	unsigned int rx2_to_tx;
	*/

/** @}*/




