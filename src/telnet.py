import telnetlib3
import time

import yaml


class Telnet:
    """
    Handles the connection via telnet. Implements some functions from
    https://developer.android.com/studio/run/emulator-console

    At the moment, we support:
     - gsm related events (incoming calls)
     - changes to the geolocation
     - incoming SMS
     - manual interaction with the client
    """

    def __init__(self,
                 telnet_host,
                 telnet_port,
                 telnet_password,
                 playbook_file) -> None:
        self.host = telnet_host
        self.port = telnet_port
        self.password = telnet_password
        self.reader = None
        self.writer = None
        self.playbook_file = playbook_file

    async def connect(self):
        reader, writer = await telnetlib3.open_connection(
            self.host, self.port)
        print(
            f"Connected to {self.host}, {self.port}")
        data = await reader.read(1024)
        print(data)
        time.sleep(2)
        writer.write("auth " + self.password + "\n")
        data = await reader.read(1024)
        print(data)
        return reader, writer

    async def execute_manual_command(self):
        # Source: https://www.geeksforgeeks.org/
        # how-to-create-telnet-client-with-asyncio-in-python/
        reader = self.reader
        writer = self.writer
        print(
            f"Connected to {self.host}, {self.port}")
        while True:
            command = input("Enter a command: ")
            if not command:
                print("No command. Closing connection")
                break
            print(f"Sending {command}\n")
            writer.write(f"{command}\n")
            time.sleep(2)
            data = await reader.read(1024)
            print(data)

    async def execute_command(self, command):
        # Source: https://www.geeksforgeeks.org/
        # how-to-create-telnet-client-with-asyncio-in-python/
        reader = self.reader()
        writer = self.writer()
        writer.write(command + "\n")
        data = await reader.read(1024)
        print(data)

    @staticmethod
    def dump_geo(yaml_file, action_id, longitude, latitude, altitude):
        yaml_file.write(yaml.dump(
            {action_id: {"TYPE": "EXTERNAL",
                         "SUBTYPE": "GEO",
                         "PARAMETERS":
                             {
                                 "LONGITUDE": longitude,
                                 "LATITUDE": latitude,
                                 "ALTITUDE": altitude}
                         }}))

    @staticmethod
    def dump_gsm(yaml_file,
                 action_id,
                 number,
                 seconds_until_accept,
                 seconds_until_end):
        yaml_file.write(yaml.dump(
            {action_id: {"TYPE": "EXTERNAL",
                         "SUBTYPE": "INCOMING_CALL_ACCEPT",
                         "PARAMETERS":
                             {"NUMBER": number,
                              "SECONDS_UNTIL_ACCEPT": seconds_until_accept,
                              "SECONDS_UNTIL_END": seconds_until_end}
                         }}))

    @staticmethod
    def dump_sms(yaml_file, action_id, number, message):
        yaml_file.write(yaml.dump(
            {action_id: {"TYPE": "EXTERNAL",
                         "SUBTYPE": "SMS",
                         "PARAMETERS":
                             {"NUMBER": number,
                              "MESSAGE": message}
                         }}))

    async def change_geo_location(self,
                                  record=True,
                                  parameters=None,
                                  yaml_file=None,
                                  action_id=None):
        if record:
            longitude = input("State the longitude. ")
            latitude = input("State the latitude. ")
            altitude = input("State the altitude. ")
            altitude = altitude if altitude != "" else 0
            Telnet.dump_geo(yaml_file,
                            action_id,
                            longitude,
                            latitude,
                            altitude)
        else:
            longitude = parameters.get("LONGITUDE")
            latitude = parameters.get("LATITUDE")
            altitude = parameters.get("ALTITUDE")
            if longitude is None or latitude is None or altitude is None:
                error_msg = ("Something went wrong. Parameter "
                             "LONGITUDE, LATITUDE, or ALTITUDE is "
                             "None: {}".format(parameters))
                return False, error_msg
        command = f"geo fix {longitude} {latitude} {altitude}"
        print(f"Sending \"{command}\" to the telnet client")
        await self.execute_command(command)

    async def incoming_call_accept(self,
                                   playbook_id,
                                   record=True,
                                   parameters=None):
        if record:
            number_calling = input("State the number that is calling. ")
            seconds_until_accept = int(
                input("After how many seconds should the call be answered? "))
            seconds_until_end = int(
                input("After how many seconds should the call be ended? "))
            output = yaml.dump(
                {playbook_id: {
                    "TYPE": "EXTERNAL",
                    "SUBTYPE": "INCOMING_CALL_ACCEPT",
                    "PARAMETERS":
                        {"NUMBER": number_calling,
                         "SECONDS_UNTIL_ACCEPT": seconds_until_accept,
                         "SECONDS_UNTIL_END": seconds_until_end}
                }})
            self.playbook_file.write(output)
        else:
            number_calling = parameters.get("NUMBER")
            seconds_until_accept = parameters.get("SECONDS_UNTIL_ACCEPT")
            seconds_until_end = parameters.get("SECONDS_UNTIL_END")
            if (number_calling is None or
                    seconds_until_accept is None or
                    seconds_until_end is None):
                error_msg = ("Something went wrong. Parameter NUMBER, "
                             "or SECONDS_UNTIL_ACCEPT, or "
                             "SECONDS_UNTIL_END is None: {}").format(
                    parameters)
                return False, error_msg
        command = f"gsm call {number_calling}"
        print(f"Sending \"{command}\" to the telnet client")
        await self.execute_command(command)
        time.sleep(seconds_until_accept)
        command = f"gsm accept {number_calling}"
        print(f"Sending \"{command}\" to the telnet client")
        await self.execute_command(command)
        time.sleep(seconds_until_end)
        command = f"gsm cancel {number_calling}"
        await self.execute_command(command)
        print(f"Sending \"{command}\" to the telnet client")

    async def incoming_call_decline(self,
                                    playbook_id,
                                    record=True,
                                    parameters=None):
        if record:
            number = input("State the number that is calling. ")
            seconds_until_decline = int(
                input("After how many seconds should the call be declined? "))
            output = yaml.dump(
                {playbook_id: {
                    "TYPE": "EXTERNAL",
                    "SUBTYPE": "INCOMING_CALL_DECLINE",
                    "PARAMETERS":
                        {"NUMBER": number,
                         "SECONDS_UNTIL_DECLINE": seconds_until_decline}
                }})
            self.playbook_file.write(output)
        else:
            number = parameters.get("NUMBER")
            seconds_until_decline = parameters.get("SECONDS_UNTIL_DECLINE")
            if number is None or seconds_until_decline is None:
                error_msg = ("Something went wrong. Parameter NUMBER, or "
                             "SECONDS_UNTIL_DECLINE is None: {}").format(
                    parameters)
                return False, error_msg
        command = f"gsm call {number}"
        print(f"Sending \"{command}\" to the telnet client")
        await self.execute_command(command)
        time.sleep(seconds_until_decline)
        command = f"gsm cancel {number}"
        print(f"Sending \"{command}\" to the telnet client")
        await self.execute_command(command)

    async def receive_sms(self,
                          playbook_id,
                          record=True,
                          parameters=None):
        if record:
            message = input("Which message do you want to receive? ")
            number = input("Number of the person sending the message: ")
            output = yaml.dump(
                {playbook_id: {"TYPE": "EXTERNAL",
                               "SUBTYPE": "SMS",
                               "PARAMETERS":
                                   {"NUMBER": number,
                                    "MESSAGE": message}
                               }})
            self.playbook_file.write(output)
        else:
            number = parameters.get("NUMBER")
            message = parameters.get("MESSAGE")
            if number is None or message is None:
                error_msg = ("Something went wrong. Parameter NUMBER, "
                             "or MESSAGE is None: {}").format(
                    parameters)
                return False, error_msg
        command = f"sms send {number} {message}"
        print(f"Sending \"{command}\" to the telnet client")
        await self.execute_command(command)
