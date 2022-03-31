from __future__ import absolute_import
from fortrace.botnet.bots.mariposa.mariposa import MariposaBot
from six.moves import input

__author__ = 'Sascha Kopp'

b = MariposaBot()
b.start()
input("Press enter to quit")
b.stop()
