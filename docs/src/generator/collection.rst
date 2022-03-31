Collections
^^^^^^^^^^^^^^^

Collections are a set of predefined variables which are used by the application to generate unpredictable traffic.

**Mail scenario**

The mail collection can receive three different parameters:

*  Recipient

*  Subjects

*  Messages

Each parameter defines a list of attributes which are used by the generator to randomize the traffic.
If you omit one of the parameters a set of default parameters is used.

.. code-block:: yaml

    collections:
      c-mail-0:
        type: mail
        recipients: ./generator/friendly_recipients.txt
        subjects: ./generator/friendly_subjects.txt
        messages: ./generator/friendly_messages.txt


**HTTP**

.. code-block:: yaml

  c-sample-name:
    type: http
    urls: urls.txt

Each line in the url.txt document represents one url.

**Printer**

.. code-block:: yaml

  c-print-0:
    type: printer
    files: files.txt

Each line in the files.txt document represents one file path.

**Samba Share**

.. code-block:: yaml

  c-smb-0:
    type: smb
    files: files.txt

Each line in the files.txt document represents one file path.
