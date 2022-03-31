from __future__ import absolute_import
from fortrace.botnet.bots.zeus.zeus import ZeusCnC
from six.moves import input

b = ZeusCnC()
b.start()
input("press enter to exit:\n")
b.stop()
