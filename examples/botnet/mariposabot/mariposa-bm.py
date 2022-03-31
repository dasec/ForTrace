from __future__ import absolute_import
from fortrace.botnet.bots.mariposa.mariposa import MariposaBotMaster
from six.moves import input

__author__ = 'Sascha Kopp'

b = MariposaBotMaster()
b.start()
input("Press enter to quit")
b.stop()
