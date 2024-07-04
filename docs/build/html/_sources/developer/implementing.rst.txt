.. _implement:

Implementing new Scenarios and Features
=========================================


#############################
Implementation of Scenarios
#############################

Implementing a scenario is quite easy. The first step should be to import all necessary modules as well as *VMM, logger, GuestListener and Reporter*
from ForTrace.

.. code-block:: python

    import time
    import logging
    import subprocess

    try:
        from fortrace.core.vmm import Vmm
        from fortrace.utility.logger_helper import create_logger
        from fortrace.core.vmm import GuestListener
        from fortrace.core.reporter import Reporter
    except ImportError as ie:
      print("Import error! in  " + str(ie))
      exit(1)


In this step, the logger is created and a virtual guest machine is cloned from the Windows template.

.. code-block:: python

    logger = create_logger('fortraceManager', logging.INFO)
    macsInUse = []
    guests = []
    guestListener = GuestListener(guests, logger)
    virtual_machine_monitor1 = Vmm(macsInUse, guests, logger)
    guest = virtual_machine_monitor1.create_guest(guest_name="test", platform="windows")



In this step, the connection between host and guest is established and the *powerShell* module is called.

.. code-block:: python

    guest.waitTillAgentIsConnected()
    ps_obj = guest.application("powerShell", {})
    subprocess.call(["virsh", "attach-device", "test", "--file", "/data/fortrace-pool/usb_device.xml"])
    time.sleep(5)

Now functions of the module can be called to create the scenario. Obviously, multiple modules can be used in one scenario.

.. code-block:: python

    ps_obj.autScripts("Bypass")
    a = "Query-fmExplorerSearch -SearchString 'motor'"
    ps_obj.pscommand(a)


###############################
Implementation of new Features
###############################

Implementing a new module requires some more work. First and foremost naming conventions are important, as module imports are dynamic.
Files should start with a lower case, classes with an upper case.

Modules contain code for two sides - what is to be executed host side and the data generation guest side. Generally this means
sending certain parameters from the host to the guest, which will then call the guest side function. There are abstract classes for
host and guest side implementation that need to be imported if this functionality is used.

.. code-block:: python

    try:
        import logging
        import sys
        import platform
        import threading
        import subprocess
        import inspect  # for listing all method of a class

        # base class VMM side
        from fortrace.application.application import ApplicationVmmSide
        from fortrace.application.application import ApplicationVmmSideCommands

        # base class guest side
        from fortrace.application.application import ApplicationGuestSide
        from fortrace.application.application import ApplicationGuestSideCommands
        from fortrace.utility.line import lineno


A *skeleton* file is prepared in the */application/* directory, which can be copied and turned into a new application module.
Alternatively, any existing module can be copied, renamed and changed.

.. autoclass:: fortrace.application.skeleton.SkeletonVmmSide
    :members:

.. autoclass:: fortrace.application.skeleton.SkeletonGuestSide
    :members:

