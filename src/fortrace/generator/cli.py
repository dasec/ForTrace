from __future__ import absolute_import
import argparse
import logging
import time

from fortrace.core.vmm import GuestListener
from fortrace.core.vmm import Vmm
from fortrace.generator import Generator
from fortrace.utility.logger_helper import create_logger


def cli():
    parser = argparse.ArgumentParser(description='Haystack generator utility.')
    parser.add_argument('config_file', type=str, help='path to the config file')
    parser.add_argument('--guest', type=str, help='name of the guest virtual machine', nargs='?',
                        default='guest-{}'.format(int(time.time())))
    parser.add_argument('--seed', type=int, help='initial seed to use for random number generation', nargs='?',
                        default=None)

    args = parser.parse_args()

    logger_core = create_logger('haystack_core', logging.ERROR)
    logger_generator = create_logger('haystack_generator', logging.INFO)

    # Create virtual machine.
    macs_in_use = []
    guests = []

    guest_listener = GuestListener(guests, logger_core)
    virtual_machine_monitor = Vmm(macs_in_use, guests, logger_core)
    guest = virtual_machine_monitor.create_guest(guest_name=args.guest, platform="windows")

    # Waiting to connect to guest.
    logger_generator.info("[~] Trying to connect to guest.")

    while guest.state != "connected":
        logger_generator.debug(".")
        time.sleep(1)

    logger_generator.info('[+] Connected to %s', guest.guestname)

    # Load and parse config file.
    generator = Generator(guest, args.config_file, logger_generator, seed=args.seed)

    # Execute action suite.
    generator.execute()

    # Todo implement function in generator to returns if dump should be created and what dump
    # todo then guest.createdump here

# TODO put entire function into generator.py so generate_haystack.py can use it to (is essentially same as this function
#    dumps = generator.dump()
#    if dumps is None:
#        logger_generator.info("No dump creation given")
#    if dumps is not None:
#        logger_generator.info("Dumps being created")
#        for i in list:
#            guest.guest_dump()
# TODO path + dump type extract, then call function
#            print(args.guest)
#            print(i)
    generator.dump()

    # Shutdown the generator before closing the VM.
    generator.shutdown()

    # Shutdown virtual machine but keep the disk.
    guest.shutdown('keep')
