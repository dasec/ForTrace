from __future__ import absolute_import
from fortrace.botnet.bots.zeus.zeus import ZeusBot
from six.moves import input

b = ZeusBot(True)  # use False if you want ip.php based nat detection (currently only static config supported)
b.start()
input("press enter to exit:\n")
b.stop()
