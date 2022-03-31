#!/usr/bin/env python
# Copyright (C) 2013-2014 Reinhard Stampp
# Copyright (C) 2014-2016 Sascha Kopp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.
from distutils.core import setup

setup(
    name='fortrace',
    version='1.0',
    packages=['fortrace', 'fortrace.attacks', 'fortrace.botnet', 'fortrace.botnet.net', 'fortrace.botnet.net.meta', 'fortrace.botnet.net.proto',
              'fortrace.core', 'fortrace.generator', 'fortrace.botnet.common', 'fortrace.botnet.core', 'fortrace.botnet.core.bmoncomponents',
              'fortrace.utility', 'fortrace.application', 'fortrace.inputDevice', 'fortrace.botnet.bots',
              'fortrace.botnet.bots.hellobot', 'fortrace.botnet.bots.mariposa', 'fortrace.botnet.bots.zeus'],
    package_dir={'fortrace': '../src/fortrace'},
    package_data={'fortrace': ['../utility/conf/*']},
    url='fortrace.fbi.h-da.de',
    license='',
    author='Reinhard Stampp, Sascha Kopp',
    author_email='reinhard.stampp@rstampp.net, sascha.kopp@stud.h-da.de',
    description='Python bindings for fortrace.'
)
