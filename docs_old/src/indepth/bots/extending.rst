.. _extending_botnet_framework:

Extending the Botnet Framework
------------------------------

This section describes how to implement templates and how to add add new templates to the framework.

Implementing the templates
--------------------------

For examples take a look at src/fortrace/botapplication .

The corresponding init-scripts can be found at /src/fortrace/botsamples .

You may want to take a look at the HelloBot as it's a POC for a completly global controlled implementation.

.. important:: You don't have to actually implement the interfaces, if you intend to make a fully standalone implementattion. Just import the interfaces and 'pass' them.

A new implementation usualy takes the following steps:

1. Recreate the botnet's protocol and implement the template-classes.
2. Create the init-scripts for each implemented bot component.
3. Create the master-control-script.

**The init-scripts:**

The init scripts usually only a few lines of code.

This includes importing the bot's modules, inititializing the bot, starting the bot and waiting for termination.

**The master-control-script:**

This script should contain the following steps:

1. Create and initialize the logger for the VirtualMachineMonitor (VMM).
2. Create the GuestListener.
3. Create the VMM.
4. Create the Guests.
5. **Important:** Wait till all guest have a valid ip-address-configuration.
6. Initialize the BotMonitor.
7. Optional: Write values to the BotMonitor's globals dict to make them available to all participants.
8. Setup groups and scripts for the BotMonitor.
9. Allocate each Guest to a group.
10. Wait for each bot-instance to receive it's payload.
11. Write your control code.


Advanced: Adding new templates
------------------------------

.. note:: The following steps will require some basic understanding with the Protocol Buffer Framework.

Adding a new template will involve the following steps.

You may want to take a look at src/fortrace/net/proto and src/fortrace/botcore for samples.

1. Add new message types to messagetypes.proto .
2. Add a new <message>.proto file for your template.
3. Compile the proto-files with the protoc-compiler.
4. Add a new module for the template class and delegate class.
