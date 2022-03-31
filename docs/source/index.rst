.. fortrace documentation master file, created by
   sphinx-quickstart on Mon Jan 20 13:14:24 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================
What is fortrace and what can it do?
==================================

fortrace is an *Open Source* python module to simulate user behaviour inside a virtual machine and like that creating
network traffic, timestamps, files and other "real world" traces one would find in a forensic case.
With this framework we opt to make data set generation accessible to the forensic community. If it is for universities
to provide students with a variety of different cases or for people creating algorithms and programs aiding forensic
investigators to test their products against.
As everything that is happening inside the virtual machine is known it can even be used to train machine learning
algorithms.

In this documentation we start by explaining how to set up fortrace.
Additionally, we will show how to use fortrace, what it can already do and how you can extend it to fit your needs.


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
