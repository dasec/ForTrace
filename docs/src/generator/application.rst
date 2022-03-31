Application
^^^^^^^^^^^
This section defines the different applications used by the fortrace generator to produce network traffic.

**Mail scenario**

Within the applications tag you can define several mail accounts.
Each mail account has an unique identifier within the applications tag.
Although the identifier does not follow any naming scheme we recommend using the provided scheme.
There are two different types of mail accounts:

* Local
   * This account uses the local SMTP and IMAP servers which are set up during the installation process (see also ..). Therefore the hostnames correspond to the IP-Addresses of the Service VM. The email address of local user is <username>@fortrace.local. **Note**: The domain maps the mydomain parameter of the postfix config file (main.cf see also..). Password and username map to the Service VM system user you created during setup. The three different socket/auth types define which ports are used for the communication to the mail server. There are three presets for the port configuration, 0=no ssl, 1=STARTTLS, 2=SSL/TLS. For the local mail delivery use 0 (if unencrypted).
* Provider
   * This account uses an official provider like Gmail, GMX etc. Be sure to use the specific settings of your mail provider.

.. code-block:: yaml

    applications:
      mail-0:
        type: mail
        imap_hostname: imap.web.de
        smtp_hostname: smtp.web.de
        email: <your_email>
        password: <your_password>
        username: <your_username>
        full_name: <your_name>
        socket_type: 3
        socket_type_smtp: 2
        auth_method_smtp: 3

**HTTP**

The application for http does not need to be configured.

**Printer**

.. code-block:: yaml

  printer-0:
    type: printer
    hostname: http://service_vm:631/ipp/print/name

Hostname is the url of the network printer. For example the printer on the
service vm.

**Samba Share**

.. code-block:: yaml

  smb-0:
    type: smb
    username: service
    password: fortrace
    destination: \\service_vm\sambashare

Username password and path of the smb share.
