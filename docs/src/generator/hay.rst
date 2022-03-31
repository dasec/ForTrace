Hay and Needles
^^^^^^^^^^^^^^^

Hay defines the inconspicuous traffic that should be generated and
needles define the suspicious traffic that should be generated.
In both sections of the configuration file action groups are assigned to applications
the arguments for the action groups can either be defined by hand or can be drawn from collections.

Each action group is defined as a YAML object, the name being the identifier of that
action group.

.. code-block:: yaml

    n-mail-sample:
        application: mail-sample

        recipient: sample@mail.com
        subject: some subject
        content: sample content

        amount: 1

Followed by the definition which application should handle this action and
arguments specific to the application.

An action block requires an amount argument that specifies how many actions
should be generated with the given parameters.

**Mail scenario**

In the hay definition you can reference a previously defined mail account via the application tag. Be sure that the referenced mail account is defined. The attachments tag is optional.

.. code-block:: yaml

    h-mail-1:
        application: mail-1
        recipient: sk@fortrace.local
        subject: a random mail
        message: I'm sending you this mail because of Y.
        attachments:
          - /data/fortrace_data/white.jpg
          - /data/fortrace_data/hda_master.pdf
        amount: 1

If you want to send several mails randomly selected from your previously defined collection, have a look at the following yaml configuration as a point of reference:

.. code-block:: yaml

    h-mail-2:
        application: mail-1
        amount: 3
        recipient: sk@fortrace.local
        collection: c-mail-0

**HTTP**

.. code-block:: yaml

    a-sample-name:
        application: http
        collection: c-sample-nam
        url: https://dasec.h-da.de/
        amount: the number of urls to open

Either a hard defined url or random urls from a collection can be used.

**Printer**

.. code-block:: yaml

  n-printer-0:
    application: printer-0
    file: C:\Users\fortrace\Documents\top_secret.txt
    collection: sample
    amount: 2

Either a file to print or a collection from which files can be selected.

**Samba Share**

.. code-block:: yaml

  n-smb-0:
    application: smb-0
    files: []
    collection: sample
    amount: 1

Either a list files or a collection.
