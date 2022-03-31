from __future__ import absolute_import
import argparse
import logging
import time
import threading

from fortrace.utility.logger_helper import create_logger
from fortrace.generator import Generator
from fortrace.core.vmm import Vmm
from fortrace.core.vmm import GuestListener
from six.moves import range

# Create logger for the Haystack core and generator.
logger_core = create_logger('haystack_core', logging.ERROR)
logger_generator = create_logger('haystack_generator', logging.DEBUG)


def start_guest(index, virtual_machine_monitor, args):
    guest = virtual_machine_monitor.create_guest(guest_name='{}-{}'.format(args.guest, index), platform="windows")

    # Waiting to connect to guest.
    logger_generator.info('[~] Trying to connect to guest {}.'.format(index))

    guest.waitTillAgentIsConnected()

    logger_generator.info('[+] Connected to %s', guest.guestname)

    # Load and parse config file.
    generator = Generator(guest, args.config_file, logger_generator, args.seed)

    # Execute action suite.
    generator.execute()

    # Shutdown the generator before closing the VM.
    generator.shutdown()

    # Shutdown virtual machine but keep the disk.
    if args.store:
        guest.shutdown('keep')
    else:
        guest.shutdown('clean')


def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Haystack generator utility.')
    parser.add_argument('config_file', type=str, help='path to the config file')
    parser.add_argument('--guest', type=str, help='name of the guest virtual machine', nargs='?',
                        default='guest-{}'.format(int(time.time())))
    parser.add_argument('--seed', type=int, help='initial seed to use for random number generation', nargs='?',
                        default=None)
    parser.add_argument('--parallel', type=int, help='amount of virtual machines running parallel', nargs='?',
                        default=1)
    parser.add_argument('--store', type=bool, help='store the virtual machine disk after shutdown', nargs='?',
                        default=False)

    args = parser.parse_args()

    # Create virtual machine.
    macs_in_use = []
    guests = []
    threads = []

    guest_listener = GuestListener(guests, logger_core)
    virtual_machine_monitor = Vmm(macs_in_use, guests, logger_core)
    for index in range(0, args.parallel):
        thread = threading.Thread(target=start_guest, args=(index, virtual_machine_monitor, args))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
