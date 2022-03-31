from __future__ import absolute_import
import argparse
import logging
import time
from fortrace.utility.logger_helper import create_logger
from fortrace.generator import Generator
from fortrace.core.vmm import Vmm
from fortrace.core.vmm import GuestListener


def main():
    # Create logger for the Haystack core and generator.
    logger_core = create_logger('haystack_core', logging.ERROR)
    logger_generator = create_logger('haystack_generator', logging.DEBUG)

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Haystack generator utility.')
    parser.add_argument('config_file', type=str, help='path to the config file')
    parser.add_argument('--guest', type=str, help='name of the guest virtual machine', nargs='?',
                        default='guest-{}'.format(int(time.time())))
    parser.add_argument('--seed', type=int, help='initial seed to use for random number generation', nargs='?',
                        default=None)

    args = parser.parse_args()

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
    generator = Generator(guest, args.config_file, logger_generator, args.seed)

    # Execute action suite.
    generator.execute()

    # Shutdown the generator before closing the VM.
    generator.shutdown()

    time.sleep(15)

    generator.execute_dumps()

    # Shutdown virtual machine but keep the disk.
    guest.shutdown('keep')


if __name__ == "__main__":
    main()
