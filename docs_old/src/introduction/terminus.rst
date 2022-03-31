================================
Terms used in this documentation
================================

While you read this documentation you may come across several keywords:

* User-/App-/Guest-Framework: The framework responsible for simulating user interactions, traffic creation and creation of guests.
* Bot-Framework: The framework responsible for simulating bot interactions and traffic creation.
* VMM: The Virtual Machine Monitor is the controller for the user-framework, see Monitor for the general term.
* Template: The master image and config for a virtual machine.
* Guest: A clone of the master image used for simulations.
* Monitor: Controller for the global simulation, will use agents to send commands to instances.
* Agent: A proxy component for instantiating instances, relaying commands and reporting status.
* Instance: A running application or simulated bot controlled by a monitor via an agent.
* New-style plugin: These refer to newly refactored application plugins for Firefox and Thunderbird (namely webBrowserFirefox.py and mailClientThunderbird.py) which use the native interfaces provided by Mozilla to control and configure the applications. 
