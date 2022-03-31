Generator
=========

The generator takes a configuration file written in YAML and hides the defined needles in
the configured hay.

Commandline usage::

    $ python -m fortrace.generator examples/example-haystack.yaml

    $ python -m fortrace.generator --help

Usage sample as a script::

    $ python examples/generate_haystack.py

Guest
^^^^^^^

At the moment the generator can only work with one guest.

Seed
^^^^

The randomness in side the generator can be seeded either using the **seed** field inside
the configuration file or using the commandline by adding the **--seed** option which
overrides the seed field. Using the same seed should result in similar network traffic.

Sections
^^^^^^^^^

.. toctree::

    collection
    application
    hay

Sample configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../examples/example-haystack.yaml
