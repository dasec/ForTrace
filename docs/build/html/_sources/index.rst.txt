.. fortrace documentation master file, created by
   sphinx-quickstart on Mon Jan 20 13:14:24 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================
What is ForTrace and what can it do?
==================================

ForTrace is an *Open Source* python framework to simulate user behaviour inside a virtual machine to create
network traffic, timestamps, files and other "real world" traces one would find in a forensic case.
With this framework we opt to make data set generation accessible to the forensic community. It can be used by universities
to provide students with a variety of different cases or by people creating algorithms and programs aiding forensic
investigators to test their products.
As everything that is happening inside the virtual machine is known and can be recorded using a **Reporting functionality** it can even be used to train machine learning
algorithms.

In this documentation we start by explaining how to set up ForTrace.
Additionally, we will show how to use ForTrace, what it can already do and how you can extend it to fit your needs.


Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   architecture/index
   architecture/framework_architecture
   architecture/generator
   architecture/service_vm
   installation/index
   installation/config
   installation/host
   installation/guest
   installation/service_vm
   installation/firstrun
   developer/index
   developer/functions
   developer/implementing




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
