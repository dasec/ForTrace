import asyncio
import argparse
import os.path

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from src.fortrace.android.synthesizer import Synthesizer
from com.dtmilano.android.viewclient import ViewClient
from com.dtmilano.android.adb.adbclient import AdbClient
from src.fortrace.android.gestures import Gestures
from src.fortrace.android.keyevents import Keyevents
from src.fortrace.android.telnet import Telnet


RECORD_SIMULATION = 1
REPLAY_SINGLE_SIMULATION = 2
REPLAY_MULTIPLE_SIMULATION = 3
EXTRACT_USERDATA_PARTITION = 98
INTERACT_WITH_TELNET_CLIENT = 99
EXIT = 100


def connect_to_device_via_adb(emulator_serialno=None):
    """
    Establish connection with the emulator over adb
    :param emulator_serialno: Serial number of the (emulated) device we want
                              to connect to
    :return: adb connection, serial number
    """
    # Connect to device
    print("Connecting to device ...")
    if emulator_serialno is None:
        emulator_serialno = ".*"
    device, serialno = ViewClient.connectToDeviceOrExit(
        verbose=True,
        serialno=emulator_serialno)
    device and print("Successfully connected to the device " + str(serialno))
    print("Serial number: " + str(serialno))
    return device, serialno


async def actions_available(synthesizer):
    global RECORD_SIMULATION
    global REPLAY_SINGLE_SIMULATION
    # global RECEIVE_SMS_USING_TELNET
    # global INCOMING_CALL_ACCEPT
    # global INCOMING_CALL_DECLINE
    # global CHANGE_GEO_LOCATION
    # global TAKE_SCREENSHOT
    global EXTRACT_USERDATA_PARTITION
    global INTERACT_WITH_TELNET_CLIENT
    global EXIT

    print("Available options:")
    print(f"{RECORD_SIMULATION}: Record Simulations")
    print(f"{REPLAY_SINGLE_SIMULATION}: Replay single scenario")
    print(f"{REPLAY_MULTIPLE_SIMULATION}: Replay multiple scenario")
    print(f"{EXTRACT_USERDATA_PARTITION}: Extract userdata partition")
    print(f"{INTERACT_WITH_TELNET_CLIENT}: Interact with the telnet client")
    print(f"{EXIT}: Exit")
    playbook_file_pointer_a = open(synthesizer.playbook_abs_file_path, "a")

    try:
        res = int(input("What do you want to do? Insert the number! "))
        if res == RECORD_SIMULATION:
            await synthesizer.record_simulation()
        elif res == REPLAY_SINGLE_SIMULATION:
            await synthesizer.replay_simulation(mode="single")
        elif res == REPLAY_MULTIPLE_SIMULATION:
            await synthesizer.replay_simulation(mode="multi")
        elif res == INTERACT_WITH_TELNET_CLIENT:
            await synthesizer.telnet.execute_manual_command()
        elif res == EXTRACT_USERDATA_PARTITION:
            synthesizer.extract_userdata_partition()
        elif res == EXIT:
            playbook_file_pointer_a.flush()
            playbook_file_pointer_a.close()
            exit(0)
        else:
            print("No valid option selected")
        playbook_file_pointer_a.flush()
    except ValueError as e:
        print(f"{e}: Input was not an integer! Try again")
    except Exception as e:
        print(f"Error occurred during the processing: {e}")


async def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--telnet_token",
                        required=True,
                        help="Authentication token for the telnet client")
    parser.add_argument("--telnet_host",
                        default="localhost",
                        required=False,
                        help="Telnet host address")
    parser.add_argument("--telnet_port",
                        default=5554,
                        required=False,
                        help="Telnet port")
    parser.add_argument("--playbook_dir",
                        default="./playbook/",
                        required=False,
                        help="Directory to store the playbooks at")
    parser.add_argument("--ground_truth",
                        default="./ground_truth/",
                        required=False,
                        help="Directory to store the ground truth file at")
    args = parser.parse_args()
    telnet_token = args.telnet_token
    telnet_host = args.telnet_host
    telnet_port = args.telnet_port
    playbook_dir = args.playbook_dir
    ground_truth_dir = args.ground_truth

    # Get absolut path for playbook_dir
    playbook_dir = os.path.abspath(playbook_dir)
    if not os.path.exists(playbook_dir):
        os.makedirs(playbook_dir)

    # Get absolut path for ground_truth_dir
    ground_truth_dir = os.path.abspath(ground_truth_dir)
    if not os.path.exists(ground_truth_dir):
        os.makedirs(ground_truth_dir)

    playbook_abs_file_path = os.path.join(playbook_dir, "config.yaml")
    playbook_abs_file_path_f_p = open(playbook_abs_file_path, "w")
    print(f"Telnet token: {telnet_token}\n"
          f"Telnet host: {telnet_host}\n"
          f"Telnet port: {telnet_port}\n"
          f"Playbook location: {playbook_dir}\n"
          f"Playbook config location: {playbook_abs_file_path}\n")

    device, serialno = connect_to_device_via_adb()
    vc = ViewClient(device=device, serialno=serialno)
    adb_client = AdbClient(serialno=serialno)

    display_attributes = device.display
    height = display_attributes.get("height")
    width = display_attributes.get("width")
    orientation = display_attributes.get("orientation")
    telnet = Telnet(telnet_host=telnet_host,
                    telnet_port=telnet_port,
                    telnet_password=telnet_token,
                    playbook_file=playbook_abs_file_path_f_p)
    telnet.reader, telnet.writer = await telnet.connect()
    gestures = Gestures(device=device,
                        height=height,
                        width=width,
                        orientation=orientation,
                        playbook_file=playbook_abs_file_path_f_p)
    keyevents = Keyevents(playbook_file=playbook_abs_file_path_f_p,
                          adb_client=adb_client)
    synthesizer = Synthesizer(viewclient=vc,
                              adbclient=adb_client,
                              device=device,
                              telnet=telnet,
                              playbook_abs_file_path=playbook_abs_file_path,
                              playbook_dir=playbook_dir,
                              ground_truth_dir=ground_truth_dir,
                              gestures=gestures,
                              keyevents=keyevents)
    while True:
        await actions_available(synthesizer)

if __name__ == "__main__":
    # There seems to be some bug with windows and event loops
    # https://stackoverflow.com/questions/
    # 45600579/asyncio-event-loop-is-closed-when-getting-loop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(start())
