Message Format
--------------

The communication between agent and VMM itself is established via a simple text protocol.
It consists of a space separated list of parameters.
The first parameter consists of the command to execute.

Communication Patterns
----------------------

The user-framework will usually conduct communication in the following pattern:

1. VMM will wait for incoming connections.
2. Guest-Agent will connect and tell interface ip- and mac-addresses.
3. VMM will send commands.
4. Guest-Agent may reply with additional data (ex. listing commands).
