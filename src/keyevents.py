import yaml


class Keyevents:
    """

    """

    def __init__(self,
                 playbook_file,
                 adb_client) -> None:
        self.playbook_file = playbook_file
        self.adb_client = adb_client

    def dump(self, playbook_id, key_event_id):
        output = yaml.dump({playbook_id: {
            "TYPE": "KEYEVENT",
            "SUBTYPE": "KEYCODE",
            "PARAMETERS":
                {"KEYCODE": key_event_id}
        }})
        self.playbook_file.write(output)

    def insert(self,
               playbook_id: int = None,
               record=True,
               key_event_id=None,
               parameters=None):
        if record:
            key_event_id = self.show_keyevents()
            self.dump(playbook_id=playbook_id,
                      key_event_id=key_event_id)

        else:
            keycode = parameters.get("KEYCODE")
            print(f"Extracted keycode {keycode}. Executing the key event")
            self.insert(False, key_event_id=keycode)
        self.adb_client.shell(f"input keyevent {key_event_id}")
        return True, None

    def show_keyevents(self):
        print("Most common key events. Insert the number "
              "for the corresponding key event. ")
        key_events_file = open("./keyevents/key_event_short.yaml", "r")
        key_events = yaml.safe_load(key_events_file)
        for key, value in key_events.items():
            print("Key event number {}:".format(key))
            for _key, _value in value.items():
                print("{}: {}".format(_key, _value))
            print("\n")

        key_event_id = int(input("Which key event do you want to execute? "
                                 "Enter 0 to show all possible key events. "))
        if key_event_id == 0:
            print("Showing all key events")
            key_events_full_file = open(
                "./keyevents/key_event_full.yaml", "r")
            print("Loading yaml information")
            key_events = yaml.safe_load(key_events_full_file)
            for key, value in key_events.items():
                print("Key event number {}:".format(key))
                for _key, _value in value.items():
                    print("{}: {}".format(_key, _value))
            key_event_id = int(
                input("Which key event do you want to execute?"))
        return key_event_id
