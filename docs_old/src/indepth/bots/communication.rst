Message Format
--------------

This section describes the use and format of messages transfered between the individual components.

For instance we use the `Link Google Protocol Buffer Framework <https://developers.google.com/protocol-buffers/>`_ (short: protobuf) for internal message encoding.

The message definitions can be found in src/fortrace/net/proto and can be compiled via the protoc-compiler.

A typical message passed between client and server contain at least the following fields:

======= ============
type    field
======= ============
uint32  length
enum    message_type
uint64  message_id
======= ============

Note that the first field is a length prefix passed onto a fully encoded message and not part of the original definition.

A specialized message can be extended with additional fields.
For example an announcement message:

======== ============
type     field
======== ============
uint32   length
enum     message_type
uint64   message_id
*enum*   *state*
*string* *instance_of*
======== ============

Communication patterns
----------------------

This section describes the basic communication patterns of the framework.

.. note:: All messages are send completely asynchronous and will be received blocking and synchronous.

1. BotMonitor will wait for incomming connections from agents.
2. Agents connect, their status will be invalid as no bot is running yet.
3. Agents will request the payload (init-scripts) for their group by default.
4. BotMonitor sends payload if registered. If not will send an empty one and Agent will try again.
5. Agent will start the BotInstance and BotInstance will announce it's state and type.
6. BotMonitor will set state and type for the connection.
7. BotInstance will request the globals dict.
8. BotMonitor will send the globals dict.
9. Initialization is done.
10. Commands can be triggered from BotMonitor's side.
11. Commands will be acknowledged and send with success state back.
