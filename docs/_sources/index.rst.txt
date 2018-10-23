.. Akela AVMU documentation master file, created by
   sphinx-quickstart on Mon Oct 15 16:17:02 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Akela AVMU's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. automodule:: avmu
   :members:

.. autoclass:: avmu.AvmuInterface
   :members:


Exceptions
==========


.. automodule:: avmu.avmu_exceptions
   :show-inheritance:
   :members:


Constants
=========

	API Constants. These are primarily passed to various arguments as literal strings.

	 | Settings for the hop-rate (e.g. time spent sampling each frequency point) in a sweep.
	 | Faster hop rates result in lower dynamic range (but faster sweeps).

	 - ``HOP_UNDEFINED`` - Hop rate not set yet
	 - ``HOP_90K``       - This rate is currently unsupported but may be enabled in the future 90K Pts/second
	 - ``HOP_45K``       - Hop rate of 45K points/second
	 - ``HOP_30K``       - Hop rate of 30K points/second
	 - ``HOP_15K``       - Hop rate of 15K points/second
	 - ``HOP_7K``        - Hop rate of 7K points/second
	 - ``HOP_3K``        - Hop rate of 3K points/second
	 - ``HOP_2K``        - Hop rate of 2K points/second
	 - ``HOP_1K``        - Hop rate of 1K points/second
	 - ``HOP_550``       - Hop rate of 550 points/second
	 - ``HOP_312``       - Hop rate of 312 points/second
	 - ``HOP_156``       - Hop rate of 156 points/second
	 - ``HOP_78``        - Hop rate of 78 points/second
	 - ``HOP_39``        - Hop rate of 39 points/second
	 - ``HOP_20``        - Hop rate of 20 points/second


	Available task states.

	 - ``TASK_UNINITIALIZED`` - Task state of uninitialized
	 - ``TASK_STOPPED``       - Task state of stopped
	 - ``TASK_STARTED``       - Task state of started
	 - ``TASK_RUNNING``       - Task state of running

	 Acquisition mode (synchronous, asynchronous) for the current acquisition

	 - ``PROG_ASYNC``  - Asynchronous acquisition mode
	 - ``PROG_SYNC``   - Synchronous acquisition mode


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
