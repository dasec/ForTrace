.. _arch:

*****************************
Framework Architecture
*****************************

This chapter will detail the key components and workflow of fortrace as well as relate the currently available features and functions.
To get a more technical overview of key functions, you can view the corresponding chapter here: :ref:`dev`.

fortrace aims to generate network traffic and further relevant digital evidence by simulating regular user generated traffic.
To accomplish this, fortrace operates as a layered system, sending requests for functions from the host to the guest layer. The guest
layer then calls the corresponding functions, simulating keystrokes and other human-to-computer interactions to create the desired network traffic.
This virtualized guest layer is realized as one or multiple virtual machine instances (clones of previously
prepared templates, see :ref:`guestinstall`) using KVM (Kernel-based Virtual Machine).
fortrace itself is programmed entirely in Python, as an OS-independent programming language was needed.


Architecture
########################

.. figure:: ../../figures/client-server-architecture.PNG
    :alt: Framework client-server architecture.

    Framework client-server architecture.

fortrace uses a common client-host architecture. The host side's **Framework Master** is used to manage and run the
virtual machines representing the guest side. The guest side is completely automated from startup to shutdown and is
run by the **Interaction Manager**, a component that simulates all inputs and keystrokes.

The figure above shows how these two components interact. The host side runs a specific scenario, which will, as a first step, create the needed guest
instances by creating clones of the appropriate virtual machine templates. Each simulated user is represented by an isolated virtual machine instance.
The framework master will then transmit the needed commands to the interaction manager of each guest, which in turn will execute these commands to generate the traffic using the application specified
in the host side scenario. As every guest is isolated, every instance can generate a separate set of traffic data.

As can be seen in the graphic, the connection between the host and client is separated from the client's
internet connection. This is done to minimize the simulation's footprint on the generated data. The IP addresses and other
related information can be adjusted in the **constants.py** file.

Additionally, the host side is used to evaluate the created traffic using the reporting function (see :ref:`architecture_index`) and the *.pcap* file
created by the automated use of **tcpdump**.


.. figure:: ../../figures/fortrace_simulation_procedure_2.png
        :alt: In-depth graphic of fortrace's data synthesis procedure.

        In-depth graphic of fortrace's data synthesis procedure.


The figure above gives a detailed step-by-step overview of the data synthesis procedure in fortrace.

1. The **vmm** class assists in setting up all needed guest environments, ensuring all functions and values are in order and creating a *listen* socket for all interfaces for the agent on all guests.

2. The **guest** class loads values from **constants.py** to create and later control the scenario-specific guest instances.

3. MAC addresses are linked to IP addresses and stored within the *libvirt* config files.

4. The *local* network for communication between guest/s and host and the network *internet* for communication between guest/s and the internet are created.

5. *Guest* class uses *libvirt* to create the guest instances specified in the input scenario with help of the prepared templates.

6. *Guest* class causes the created guest instances to load their respective interaction models.

7. The interaction models are executed - this means the virtual machines are started and *tcpdump* begins recording all traffic.

8. The guest instances are connected to the virtual machines.

9. The traffic within each VM is generated through the interaction manager's execution of the respective scenarios.

10. The scenarios have completed and the simulation is over. *Tcpdump* stops recording and the virtual machines are shut down.

11. The virtual machines and network interfaces are deleted.

The following diagram gives some additional insight into the workflow of a general simulation lifecycle.

.. figure:: ../../figures/fortrace-workflow.png
        :alt: General fortrace workflow.

        General fortrace workflow.






Features and Functions
#######################

To run fortrace, we recommend a Ubuntu host machine. The virtualized guests fortrace is currently capable of using to generate
traffic are Ubuntu, Windows 7 and Windows 10. Additionally, fortrace supports the following common (network) applications for
traffic generation:

+------------------------------+-----------------+----------------+------------+
|Function                      |Protocol         | Windows 7/10   | Ubuntu     |
+==============================+=================+================+============+
|Firefox Browse URL            |HTTP/HTTPS       |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Firefox Click Element         |HTTP/HTTPS       |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Firefox Download              |HTTP/HTTPS       |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Thunderbird receive Email     |POP3/IMAP/IMAPS  |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Thunderbird send Email        |SMTP/SMTPS       |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Thunderbird fill mailbox file |-                |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|VeraCrypt create container    |-                |Yes             |Not tested  |
+------------------------------+-----------------+----------------+------------+
|VeraCrypt un-/mount container |-                |Yes             |Not tested  |
+------------------------------+-----------------+----------------+------------+
|Execute console commands      |-                |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Change system clock           |-                |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|Multiuser capability          |-                |Yes             |No          |
+------------------------------+-----------------+----------------+------------+
|SSH connection/file transfer  |SSH/SFTP         |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|SMB file transfer             |SMB              |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+
|IPP print job                 |IPP              |Yes             |Yes         |
+------------------------------+-----------------+----------------+------------+

fortrace is able to use *Firefox* to perform common web browsing actions to generate traffic such as browsing to and navigating
webpages, e.g. browsing to a video or audio streaming site. fortrace is also able to download files from websites. Navigation
of a page can be performer through multiple ways, including the use of xpath variables.

With the *Thunderbird* application fortrace is able to perform common email tasks such as sending and receiving emails as well as
logging into an email account of the user's choice. The *service VM* contains a mailserver that can be used to send unencrypted
mails. This allows analysis of both mail traffic and content.

*SSH/SFTP* protocols are usable by fortrace to transfer data from or to servers. fortrace is built with the capability to use both
Linux Bash and Windows command line.

*VeraCrypt* has been implemented as a tool to generate images rather than network traffic. As of right now, image generation
is only possible for Windows guests.

Multiple common *Botnet simulation attacks* such as Mariposa, Zeus, Asprox or Waledac have already been implemented into
fortrace to generate network dumps of an attack from the victim's side. It is also possible to add new attack variants.


*SMB file transfer* uses the tool **Samba** to move data to a network drive. This drive is located on the service VM. Since
SMB file transfers are usually not encrypted, the traffic and content can be easily analyzed.

*IPP print job* is a simulation of an attack in which confidential documents are printed through a network printer.
For this, the service VM is set up with **ippserver** as a virtual network printer.

.. TODO: add some explanation to SMB file transfer & IPP print job?


==================================
Image Generation
==================================

.. figure:: ../../figures/fortrace_framework_image_generator.png
    :alt: Persistent image generation with fortrace.

    Persistent image generation with fortrace.

Besides generating network traffic, fortrace also allows for the creation of persistent disk image generation.
As the figure above shows, fortrace is able to simulate the use of several common user applications. In addition to that,
fortrace can manipulate the system clock to simulate system usage over user-chosen time interval. To track all modifications
applied to a disk image, fortrace provides a log file with all relevant information and hash sums. The generated images are distributed
in the *qemu* format, meaning they are smaller snapshots of a larger base image, limiting the required disk space.













