from __future__ import absolute_import
from fortrace.botnet.bots.mariposa.mariposa import MariposaCnC
from six.moves import input

__author__ = 'Sascha Kopp'

b = MariposaCnC()
b.start()
input("Press enter to quit")
b.stop()
