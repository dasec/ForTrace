import os
import subprocess
import sys
import time
import yaml

from datetime import datetime

# Define some global variables
RECORD_SIMULATION_SELECT_VIEW_ELEMENT = 1
RECORD_SIMULATION_PERFORM_GESTURE = 2
RECORD_SIMULATION_CHANGE_GPS = 3
RECORD_SIMULATION_INITIATE_CALL_DECLINE = 4
RECORD_SIMULATION_INITIATE_CALL_ACCEPT = 5
RECORD_SIMULATION_RECEIVE_SMS = 6
RECORD_SIMULATION_INSERT_KEYEVENT = 7
RECORD_SIMULATION_INSERT_TEXT = 8
RECORD_END = 100


def _process_nodes(root_tree,
                   user_id=0,
                   indent=0,
                   lst_of_views=[],
                   recording=False):
    """
    Given the root tree, which represents the hierarchical view of the UI
    elements on the display, this function extracts all information needed
    for further interaction with the user. That is, it extracts all necessary
    information from each node (view object) of the tree (ID, Package Name,
    Class, etc.) and returns this information as a dictionary that we can
    present to the user

    :param root_tree: Tree like structure containing the views that represent
                      the displayed UI elements
    :param user_id: ID that is assigned to a node
    :param indent: Indentation used if recording is set to True
    :param lst_of_views: List of views
    :param recording: Print result if set to True

    :return: A dictionary containing all nodes of the current root tree
             enriched with information that can be presented to the user
    """
    if lst_of_views is None:
        lst_of_views = []
    attribute_map_dic = root_tree.map
    rsrc_class = attribute_map_dic.get("class")
    rsrc_clickable = attribute_map_dic.get("clickable")
    rsrc_view = root_tree
    rsrc_package_name = attribute_map_dic.get("package")
    if root_tree.getId() is None or root_tree.getId() == "":
        _id = "None"
    else:
        _id = root_tree.getId()

    if root_tree.getContentDescription() is None or \
            root_tree.getContentDescription() == "":
        _content_description = "None"
    else:
        _content_description = root_tree.getContentDescription()

    if root_tree.getText() is None or root_tree.getText() == "":
        _text = "None"
    else:
        _text = root_tree.getText()
    if root_tree.getTag() is None or root_tree.getTag() == "":
        _tag = "None"
    else:
        _tag = root_tree.getTag()

    recording and print(
        "{}ID: {}, CLASS: {}, ID: {}, TEXT: {}, TAG: {}, clickable: {}, "
        "CONTENT_DESCRIPTION: {}, package_name: {}".format(
            " " * indent * 2,
            user_id,
            rsrc_class, _id,
            _text, _tag,
            rsrc_clickable,
            _content_description,
            rsrc_package_name
        ))

    res = dict(ID_USER_SELECTION=user_id, RESOURCE_CLICKABLE=rsrc_clickable,
               RESOURCE_CLASS=rsrc_class, RESOURCE_ID=_id,
               RESOURCE_TEXT=_text,
               RESOURCE_CONTENT_DESCRIPTION=_content_description,
               RESOURCE_TAG=_tag,
               RESOURCE_PACKAGE_NAME=rsrc_package_name, VIEW=rsrc_view,
               RESOURCE_CHILD=[])
    lst_of_views.append(res)
    for child in root_tree.children:
        lst_elem, user_id, _lst_of_views = _process_nodes(child,
                                                          user_id + 1,
                                                          indent + 1,
                                                          [],
                                                          recording=recording)
        res["RESOURCE_CHILD"].append(lst_elem)
        lst_of_views.append(res)
    return res, user_id, lst_of_views


def process_nodes(root_tree, recording=False):
    """
    Handles the processing of _process_nodes. _process_nodes extracts
    information from each node-view object and returns the tree as a
    dictionary

    :param root_tree: Tree like structure containing the views that represent
                      the displayed UI elements
    :param recording: If set to True, we will print the hierarchy during the
                      processing

    :return: A dictionary containing all nodes of the current root tree
             enriched with information that can be presented to the user
    """
    res, _, _ = _process_nodes(root_tree,
                               user_id=0,
                               indent=0,
                               lst_of_views=[],
                               recording=recording)
    return res


def select_matching_node(root_tree, selected_node_id):
    """
    Given a dictionary that contains all processed nodes of a tree,
    this function returns the node that was selected by the user

    :param root_tree: The root tree (result of process_nodes)
    :param selected_node_id: The id of the node that has been selected by
                             the user

    :return: The actual result containing all necessary information to
             be able to replay the scenario later on
    """
    id_user_selection = root_tree["ID_USER_SELECTION"]
    res = root_tree
    match = False
    editText = False
    selected_view = None
    if id_user_selection == selected_node_id:
        selected_view = root_tree["VIEW"]
        root_tree["RESOURCE_CHILD"] = []
        return res, True, True if "EditText" in res[
            "RESOURCE_CLASS"] else False, selected_view
    elif id_user_selection < selected_node_id:
        for child in root_tree.get("RESOURCE_CHILD"):
            (res["RESOURCE_CHILD"],
             match,
             editText,
             selected_view) = select_matching_node(child, selected_node_id)
            if match:
                return res, match, editText, selected_view
    else:
        print("Something went wrong when looking up the matching node")
        sys.exit(0)
    return res, match, editText, selected_view


class Synthesizer:
    """
    Synthesizer Class
    """

    def __init__(self,
                 viewclient,
                 adbclient,
                 device,
                 telnet,
                 playbook_abs_file_path,
                 playbook_dir,
                 ground_truth_dir,
                 gestures,
                 keyevents):
        self._viewclient = viewclient
        self._adbclient = adbclient
        self._device = device
        self._telnet_reader, self._telnet_writer = None, None
        self.playbook_abs_file_path = playbook_abs_file_path
        self._playbook_dir = playbook_dir
        self._playbook_exec_config = os.path.join(playbook_dir,
                                                  "exec_order.yaml")
        self.ground_truth_dir = ground_truth_dir
        self.ground_truth_file = os.path.join(ground_truth_dir,
                                              "ground_truth.yaml")
        self._counter = 0
        self.gesture = gestures
        self.telnet = telnet
        self.keyevent = keyevents

    def get_playbook_exec_order_config(self):
        return self._playbook_exec_config

    def get_counter_and_increment(self):
        tmp = self._counter
        self.inc_counter()
        return tmp

    def inc_counter(self):
        self._counter += 1

    def _convert_action_to_yaml_output(self, selected_view_dic,
                                       text_to_insert):
        """
        Does the actual convertion of the pressing of an UI element to valid
        yaml output format. This function processes each node until it reaches
        the pressed (leaf) node and converts each node along the way to a dict

        :param selected_view_dic: The dictionary that contains the attributes
                                  of the pressed UI element
        :param text_to_insert: If the selected UI element allows the user
                               to insert text (e.g. when interacting with
                               EditTexts), the inserted text is also stored
        :return: Tuple of the converted tree and the subtype of the view
        """
        view_id = selected_view_dic.get("RESOURCE_ID")
        txt = selected_view_dic.get("RESOURCE_TEXT")
        cont_descr = selected_view_dic.get("RESOURCE_CONTENT_DESCRIPTION")
        tag = selected_view_dic.get("RESOURCE_TAG")
        class_type = selected_view_dic.get("RESOURCE_CLASS")
        pkg_name = selected_view_dic.get("RESOURCE_PACKAGE_NAME")
        child = selected_view_dic.get("RESOURCE_CHILD")
        subtype = None
        res = dict(RESOURCE_ID=view_id, RESOURCE_TEXT=txt,
                   RESOURCE_CONTENT_DESCRIPTION=cont_descr,
                   RESOURCE_TAG=tag,
                   RESOURCE_CLASS=class_type,
                   RESOURCE_PACKAGE_NAME=pkg_name,
                   RESOURCE_CHILD=[])
        if not len(child) > 0:
            res[
                "TEXT_TO_INSERT"] = text_to_insert \
                if text_to_insert is not None else "None"
            subtype = class_type
        else:
            child, subtype = self._convert_action_to_yaml_output(
                child, text_to_insert)
            res["RESOURCE_CHILD"].append(child)
        return res, subtype

    def convert_view_action_to_yaml_output(self,
                                           selected_view_dic,
                                           text_to_insert):
        """
        Convert the pressing of an UI element to valid yaml output format

        :param selected_view_dic: The dictionary that contains the attributes
                                  of the pressed UI element
        :param text_to_insert: If the selected UI element allows the user
                               to insert text (e.g. when interacting with
                               EditTexts), the inserted text is also stored
        :return: Valid yaml output that can be dumped to a file
        """
        converted, subtype = self._convert_action_to_yaml_output(
            selected_view_dic, text_to_insert)
        if subtype is None:
            print("WARNING. Subtype should not be None")
        output = yaml.dump(
            {self.get_counter_and_increment(): {"PARAMETERS": converted,
                                                "TYPE": "VIEW",
                                                "SUBTYPE": subtype}},
            sort_keys=False)
        return output

    def change_playbook_file(self):
        pass

    def load_playbook(self, playbook_to_load):
        """
        Opens the playbook and returns its content

        :param playbook_to_load: Absolute path to the playbook file

        :return: Scenario stored in the playbook_file
        """
        print(f"Trying to open {playbook_to_load}")
        print("Loading yaml information")
        playbook_file_pointer = open(playbook_to_load, "r")
        scenario = yaml.safe_load(playbook_file_pointer)
        print("Collecting information from yaml")
        scenario_name = scenario.pop("NAME")
        scenario_description = scenario.pop("DESCRIPTION")
        # amount_of_actions = scenario.pop("AMOUNT_OF_ACTIONS")
        print("Loaded scenario \"{}\". Description: \"{}\"".format(
            scenario_name, scenario_description))
        return scenario

    def create_new_scenario(self):
        """
        Handles the user interaction to create a new scenario
        """
        scenario_name = input(
            "Under which name do you want to save the record? ")
        scenario_description = input("Which description do you want to add? ")
        scenario_name = scenario_name if scenario_name != "" else "UNDEFINED"
        scenario_description = scenario_description if \
            scenario_description != "" else "UNDEFINED"
        playbook_file_pointer_a = open(self.playbook_abs_file_path, "a")
        playbook_file_pointer_a.write(yaml.dump({"NAME": scenario_name}))
        playbook_file_pointer_a.write(
            yaml.dump({"DESCRIPTION": scenario_description}))
        playbook_file_pointer_a.close()

    async def record_simulation(self):
        """
        Interacts with the user during the recording of a scenario
        """
        print("Each record is started from the home screen to avoid errors")
        self._device.press("KEYCODE_HOME")
        print("Waiting 2 seconds so that the home view can load")
        time.sleep(2)

        # Store information about the scenario
        self.create_new_scenario()
        while True:
            print(f"{RECORD_SIMULATION_SELECT_VIEW_ELEMENT}: "
                  f"Select view element")
            print(f"{RECORD_SIMULATION_PERFORM_GESTURE}: Perform gesture")
            print(f"{RECORD_SIMULATION_CHANGE_GPS}: Change GPS")
            print(f"{RECORD_SIMULATION_INITIATE_CALL_DECLINE}: "
                  f"Initiate Call (decline)")
            print(f"{RECORD_SIMULATION_INITIATE_CALL_ACCEPT}: "
                  f"Initiate Call (accept)")
            print(f"{RECORD_SIMULATION_RECEIVE_SMS}: Receive SMS")
            print(f"{RECORD_SIMULATION_INSERT_KEYEVENT}: Insert key event")
            print(f"{RECORD_SIMULATION_INSERT_TEXT}: Insert text")
            print(f"{RECORD_END}: End recording")
            answer = int(input("Which action do you want to execute? "))
            if answer == RECORD_SIMULATION_SELECT_VIEW_ELEMENT:
                self.record_select_view_element()
            elif answer == RECORD_SIMULATION_PERFORM_GESTURE:
                self.gesture.record_perform_gesture(
                    playbook_id=self.get_counter_and_increment()
                )
            elif answer == RECORD_SIMULATION_CHANGE_GPS:
                await self.telnet.change_geo_location(
                    playbook_id=self.get_counter_and_increment()
                )
            elif answer == RECORD_SIMULATION_INITIATE_CALL_DECLINE:
                await self.telnet.incoming_call_decline(
                    playbook_id=self.get_counter_and_increment()
                )
            elif answer == RECORD_SIMULATION_INITIATE_CALL_ACCEPT:
                await self.telnet.incoming_call_accept(
                    playbook_id=self.get_counter_and_increment()
                )
            elif answer == RECORD_SIMULATION_RECEIVE_SMS:
                await self.telnet.receive_sms(
                    playbook_id=self.get_counter_and_increment()
                )
            elif answer == RECORD_SIMULATION_INSERT_KEYEVENT:
                self.keyevent.insert(
                    playbook_id=self.get_counter_and_increment()
                )
            elif answer == RECORD_SIMULATION_INSERT_TEXT:
                self.insert_text()
            elif answer == RECORD_END:
                break

    async def _replay_simulation(self, playbook, delay: int = 4):
        """
        Given a playbook, this function handles the execution of each action
        within the scenario by calling its respective function

        :param playbook: Absolute path to the playbook file
        :return:
        """
        f_ground_truth = open(self.ground_truth_file, "a")
        scenario = self.load_playbook(playbook)
        print(
            "Returning to the home screen before starting with the simulation")
        self._device.press("KEYCODE_HOME")
        print("Wait for 2 seconds for the new view to load")
        time.sleep(2)
        for key, value in scenario.items():
            ground_truth_output = {}
            try:
                print(f"Trying to simulate {key}: {value}")

                # Store the time stamp of the simulation of the single action
                ground_truth_output["Simulation_start"] = datetime.now()
                ground_truth_output["Action"] = f"{key}: {value}"

                # Read stored details
                parameters = value.get("PARAMETERS")
                type_of_action = value.get("TYPE")
                subtype_of_action = value.get("SUBTYPE")

                if type_of_action == "EXTERNAL":
                    success, error_msg = await self.replay_external(
                        subtype_of_action, parameters)
                elif type_of_action == "GESTURES":
                    success, error_msg = self.gesture.replay_gesture(
                        subtype_of_action)
                elif type_of_action == "VIEW":
                    success, error_msg = self.replay_view(parameters)
                elif type_of_action == "KEYEVENT":
                    success, error_msg = self.keyevent.insert(
                        record=False,
                        parameters=parameters)
                elif type_of_action == "TEXT":
                    success, error_msg = self.insert_text(
                        recording=False,
                        parameters=parameters)
                else:
                    print(f"Unable to determine the type of the action:"
                          f" {key}: {value}")
                    break
                if not success:
                    print(f"Error during the simulation of {key}: "
                          f"{value}. Error: {error_msg}")
                else:
                    print(f"Finished simulation of {key}: {value}")
                    ground_truth_output["Status"] = "SUCCESS"
                    time.sleep(delay)
            except Exception as e:
                print(f"Error during the simulation of {key} - {value}\n"
                      f"Error: {e}")
                ground_truth_output["Status"] = "ERROR"
            ground_truth_output["Simulation_end"] = datetime.now()
            f_ground_truth.write(yaml.dump(ground_truth_output))
        return True

    async def replay_simulation(self, mode="single"):
        """
        Handles the distinction between the two modes single and multi

        :param mode: Indicates whether we are executing a single playbook
                     or multiple playbooks. Default: single
        :return:
        """
        if mode == "single":
            # Single playbook is being replayed
            playbook = str(input(f"State the playbook to execute. "
                                 f"Default: {self.playbook_abs_file_path}"))
            playbook = playbook if playbook != "" \
                else self.playbook_abs_file_path
            if not os.path.isfile(playbook):
                print("Given path does not represent a file. "
                      "Returning to the main menu")
                return False
            print(f"Executing single playbook \"{playbook}\"")
            return await self._replay_simulation(playbook)
        elif mode == "multi":
            # Multiple playbooks are being replayed
            # We are now loading a configuration file that
            # defines the playbooks and order to execute
            playbook_exec_order = str(input(
                f"Enter the filename of the file that contains the "
                f"playbooks and its order to execute."
                f"Default: {self.get_playbook_exec_order_config()}"))
            playbook_exec_order = playbook_exec_order if \
                playbook_exec_order != "" \
                else self.get_playbook_exec_order_config()
            if not os.path.isfile(playbook_exec_order):
                print("Given path does not represent a file. "
                      "Returning to the main menu")
                return False
            print(f"Reading the execution order from {playbook_exec_order}")
            exec_order_file = open(playbook_exec_order, "r")
            exec_order = yaml.safe_load(exec_order_file)
            res_lst = []
            for order, parameter in exec_order.items():
                playbook = parameter.get("FILENAME")
                playbook = os.path.join(self._playbook_dir, playbook)
                if os.path.isfile(playbook):
                    res = await self._replay_simulation(playbook)
                    res_lst.append(res)
                    self._device.press("KEYCODE_HOME")
                    time.sleep(2)
                else:
                    print("Extracted file is not a config. Returning")
                    return False
        return True

    async def replay_external(self, subtype_of_action, parameters):
        """
        Handles the replay of an external event

        :param subtype_of_action: Subtype of the loaded external feature
        :param parameters: Parameter that contains more information about the
                           loaded subtype (e.g. number, geolocation, etc.)
        :return: Status code and error message
        """
        error_msg = None
        try:
            if subtype_of_action == "GEO":
                await self.telnet.change_geo_location(
                    record=False,
                    parameters=parameters)
                return True, error_msg
            elif subtype_of_action == "INCOMING_CALL_DECLINE":
                await self.telnet.incoming_call_decline(
                    record=False,
                    parameters=parameters)
                return True, error_msg
            elif subtype_of_action == "INCOMING_CALL_ACCEPT":
                await self.telnet.incoming_call_accept(
                    record=False,
                    parameters=parameters)
                return True, error_msg
            elif subtype_of_action == "SMS":
                await self.telnet.receive_sms(
                    record=False,
                    parameters=parameters)
                return True, error_msg
        except Exception as e:
            return False, e

    def replay_view_search_backup(self, root_tree, last_node):
        """
        If the tree structure changed for whatever reason and no matching
        node was determined, we will try to loop over each single node to
        look for potential matching nodes

        :param root_tree: The current view hierarchy
        :param last_node: Information about the last node that we try to match

        :return: TODO
        """
        last_node_id = last_node.get("RESOURCE_ID")
        last_node_txt = last_node.get("RESOURCE_TEXT")
        last_node_cont_descr = last_node.get("RESOURCE_CONTENT_DESCRIPTION")
        last_node_tag = last_node.get("RESOURCE_TAG")
        last_node_class = last_node.get("RESOURCE_CLASS")
        last_node_pkg_name = last_node.get("RESOURCE_PACKAGE_NAME")
        last_node_txt_to_insert = last_node.get("TEXT_TO_INSERT")
        for child in root_tree.get("RESOURCE_CHILD"):
            subtree_id = child.get("RESOURCE_ID")
            subtree_txt = child.get("RESOURCE_TEXT")
            subtree_cont_descr = child.get("RESOURCE_CONTENT_DESCRIPTION")
            subtree_tag = child.get("RESOURCE_TAG")
            subtree_class = child.get("RESOURCE_CLASS")
            subtree_pkg_name = child.get("RESOURCE_PACKAGE_NAME")
            subtree_view = child.get("VIEW")
            if subtree_pkg_name == last_node_pkg_name \
                    and subtree_class == last_node_class \
                    and subtree_id == last_node_id \
                    and subtree_txt == last_node_txt \
                    and subtree_cont_descr == last_node_cont_descr \
                    and subtree_tag == last_node_tag:
                subtree_view.touch()
                if "EDITTEXT" in subtree_class.upper():
                    print(
                        "Detected EditText view element. Sleep for 2 seconds, "
                        "insert the text and sleep again for 2 seconds")
                    time.sleep(2)
                    self._device.type(last_node_txt_to_insert)
                    time.sleep(2)
                    print("Pressing enter and waiting for it "
                          "to load for two seconds")
                    self._device.press("KEYCODE_ENTER")
                return True
            else:
                res = self.replay_view_search_backup(child, last_node)
                if res:
                    # TODO Return value set for each possibility?
                    return res

    def replay_view_process_dic(self, stored_tree, last_node,
                                root_tree_processed_lst):
        """
        Tries to match the elements of the stored tree (from the root node
        down to the last node) with the processed view of the current
        hierarchy

        :param stored_tree: The tree that was stored in the playbook
        :param last_node: The last node of the stored tree of the playbook
        :param root_tree_processed_lst:

        :return: True if we were successful to find all matching elements,
                 false otherwise
        """
        stored_id = stored_tree.get("RESOURCE_ID")
        stored_text = stored_tree.get("RESOURCE_TEXT")
        stored_cont_desc = stored_tree.get("RESOURCE_CONTENT_DESCRIPTION")
        stored_tag = stored_tree.get("RESOURCE_TAG")
        stored_class = stored_tree.get("RESOURCE_CLASS")
        stored_pkg_name = stored_tree.get(
            "RESOURCE_PACKAGE_NAME")
        stored_child = stored_tree.get("RESOURCE_CHILD")
        stored_txt_to_ins = stored_tree.get("TEXT_TO_INSERT")
        res = False
        for node in root_tree_processed_lst:
            node_id = node.get("RESOURCE_ID")
            node_txt = node.get("RESOURCE_TEXT")
            node_cont_desc = node.get("RESOURCE_CONTENT_DESCRIPTION")
            node_tag = node.get("RESOURCE_TAG")
            node_class = node.get("RESOURCE_CLASS")
            node_pkg_name = node.get("RESOURCE_PACKAGE_NAME")
            node_child = node.get("RESOURCE_CHILD")
            node_view = node.get("VIEW")
            if node_pkg_name == stored_pkg_name \
                    and node_class == stored_class \
                    and node_id == stored_id \
                    and node_txt == stored_text \
                    and node_cont_desc == stored_cont_desc \
                    and node_tag == stored_tag:
                if len(stored_child) == 0:
                    node_view.touch()
                    if "EDITTEXT" in node_class.upper():
                        print(
                            "Detected EditText view element. Sleep for "
                            "2 seconds, insert the text and sleep "
                            "again for 2 seconds")
                        time.sleep(2)
                        self._device.type(stored_txt_to_ins)
                        time.sleep(2)
                        print(
                            "Pressing enter and waiting for "
                            "it to load for two seconds")
                        self._device.press("KEYCODE_ENTER")
                    return True
                elif len(node_child) > 0 and len(stored_child) > 0:
                    res = self.replay_view_process_dic(
                        stored_child[0],
                        last_node,
                        node_child)
                    if res:
                        return True
                else:
                    print("Found node with same attributes as current node. "
                          "However, we are not at the last child node of our "
                          "stored tree")
            last_node_id = last_node.get("RESOURCE_ID")
            last_node_txt = last_node.get("RESOURCE_TEXT")
            last_node_cont_desc = last_node.get("RESOURCE_CONTENT_DESCRIPTION")
            last_node_tag = last_node.get("RESOURCE_TAG")
            last_node_class = last_node.get("RESOURCE_CLASS")
            last_node_pkg_name = last_node.get("RESOURCE_PACKAGE_NAME")
            last_node_to_insert = last_node.get("TEXT_TO_INSERT")
            if node_pkg_name == last_node_pkg_name \
                    and node_class == last_node_class \
                    and node_id == last_node_id \
                    and node_txt == last_node_txt \
                    and node_cont_desc == last_node_cont_desc \
                    and node_tag == last_node_tag:
                if "EDITTEXT" in node_class.upper():
                    node_view.touch()
                    print(
                        "Detected EditText view element. Sleep for 2 seconds, "
                        "insert the text and sleep again for 2 seconds")
                    time.sleep(2)
                    self._device.type(last_node_to_insert)
                    time.sleep(2)
                    print("Pressing enter and waiting for "
                          "it to load for two seconds")
                    self._device.press("KEYCODE_ENTER")
                print("Found backup")
                return True
        return res

    def get_last_node_of_tree(self, stored_tree):
        """
        Return the last node of the tree

        :param stored_tree: The tree that was stored within the playbook
        :return: The last node of the tree with all its attributes
        """
        last_node_id = stored_tree.get("RESOURCE_ID")
        last_node_txt = stored_tree.get("RESOURCE_TEXT")
        last_node_cont_desc = stored_tree.get("RESOURCE_CONTENT_DESCRIPTION")
        last_node_tag = stored_tree.get("RESOURCE_TAG")
        last_node_class = stored_tree.get("RESOURCE_CLASS")
        last_node_pkg_name = stored_tree.get("RESOURCE_PACKAGE_NAME")
        last_node_child = stored_tree.get("RESOURCE_CHILD")
        last_node_txt_to_insert = stored_tree.get("TEXT_TO_INSERT")
        for child in last_node_child:
            return self.get_last_node_of_tree(child)
        last_node = {"RESOURCE_ID": last_node_id,
                     "RESOURCE_TEXT": last_node_txt,
                     "RESOURCE_CONTENT_DESCRIPTION": last_node_cont_desc,
                     "RESOURCE_TAG": last_node_tag,
                     "RESOURCE_CLASS": last_node_class,
                     "RESOURCE_PACKAGE_NAME": last_node_pkg_name,
                     "RESOURCE_CHILD": last_node_child,
                     "TEXT_TO_INSERT": last_node_txt_to_insert}
        return last_node

    def replay_view(self, stored_tree):
        """
        Handles the replay of view elements

        :param stored_tree: The tree that was stored in the playbook
        :return: Status code and error message
        """
        error_msg = None
        self._viewclient.dump()
        root_tree_processed = process_nodes(
            self._viewclient.getRoot())
        stored_tree_last_node = self.get_last_node_of_tree(stored_tree)
        res = self.replay_view_process_dic(stored_tree,
                                           stored_tree_last_node,
                                           [root_tree_processed])
        # Try to find last node within the tree
        if not res:
            print(
                "Unable to find original tree. Looking for matching sub node")
        res = res if res else self.replay_view_search_backup(
            root_tree_processed,
            stored_tree_last_node)
        if not res:
            success = False
            error_msg = "Unable to replay the action"
            return success, error_msg
        else:
            print("Successfully replayed the action")
            success = True
            return success, error_msg

    def insert_text(self, recording=True, parameters=None):
        """
        Insert text into the view that is currently in focus

        :param recording: States if we are currently recording or simulating.
                          Default: True
        :param parameters: Parameters that are stored within the playbook
        :return: Status code and error message
        """
        success = False
        error_msg = None
        if recording:
            text_to_insert = str(input(
                "Which text do you want to insert into "
                "the field the cursor is currently at? "))
            output = yaml.dump(
                {self.get_counter_and_increment(): {"TYPE": "TEXT",
                                                    "SUBTYPE": "INSERT",
                                                    "PARAMETERS": {
                                                        "TEXT": text_to_insert
                                                    }}})
            playbook_file_pointer = open(self.playbook_abs_file_path, "a")
            playbook_file_pointer.write(output)
            playbook_file_pointer.close()
        else:
            text_to_insert = parameters.get("TEXT")
            print(f"Extracted text to insert: {text_to_insert}")
        # Temporary solution to enable line breaks
        text_to_insert = text_to_insert.replace("\\n", "\n")
        # self.get_adbclient().shell(f"input text \"{text_to_insert}\"")
        self._device.type(text_to_insert)
        self._device.press("KEYCODE_ENTER")
        return success, error_msg

    def restart_adb_as_root(self):
        """
        Restart Android Debug Bridge as root

        :return: True if we are root, otherwise False
        """
        print("Restarting adb as root")
        process = subprocess.Popen(["adb", "root"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(f"Stdout: {str(stdout.decode('utf-8'))}")
        time.sleep(5)
        # Check if we are root
        process = subprocess.Popen(["adb", "shell", "id"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout = str(stdout.decode('utf-8'))
        if "(root)" in stdout:
            print(f"Restart as root successful: {stdout}")
            return True
        else:
            print(f"Something went wrong. We are still not root: {stdout}")
            return False

    def create_userdata_backup(self, curr_date):
        """
        Creates a backup of the userdata folder /data and stores its result
        as [curr_date].tar

        :param curr_date: The current date/timestamp

        :return: The name of the created backup
        """
        backup_name = str(curr_date) + ".tar"
        stmt = ("tar -vcf /sdcard/archive_" + backup_name +
                "/data 1 2>sdcard/backup_log.txt")

        print(f"Start creating backup at "
              f"{str(datetime.today().strftime('%Y%m%d-%H%M%S'))}: {stmt}")
        response = self._device.type(stmt)
        print(response)
        print("Waiting for 2 minutes for the creation of the backup")
        time.sleep(120)
        return backup_name

    def copy_userdata_backup_to_disc(self, backup_name, backup_path):
        """
        Copy backup_name from the (emulated) device to backup_path

        :param backup_name: Name of the backup that has been created
                            on the device
        :param backup_path: Local directory where we store the backup
        """
        print("Start copying backup")
        process = subprocess.Popen(
            ["adb", "pull", "/sdcard/archive_" + backup_name,
             backup_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print("Stdout: {}".format(str(stdout.decode("utf-8"))))

        print("Start copying backup log")
        process = subprocess.Popen(
            ["adb", "pull", "/sdcard/backup.log", backup_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print("Stdout: {}".format(str(stdout.decode("utf-8"))))

    def extract_userdata_partition(self):
        """
        Extract the user data partition
        """
        # Restarting adb as root
        success = self.restart_adb_as_root()
        if not success:
            return

        # Create backup directory if it does not exist
        backup_path = "./backup/"
        backup_path = os.path.join(os.getcwd(), backup_path)
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        # Extract userdata partition
        curr_date = datetime.today().strftime("%Y%m%d-%H%M%S")
        backup_name = self.create_userdata_backup(curr_date=curr_date)
        print(f"Done creating backup \"{backup_name}\"."
              f"Copying backup to {backup_path}")
        self.copy_userdata_backup_to_disc(backup_name, backup_path)

        # Restarting adb as non-root
        print("Restarting adb as non root")
        process = subprocess.Popen(["adb", "unroot"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(f"Stdout: {str(stdout.decode('utf-8'))}")

    def record_select_view_element(self):
        """
        Handles the interaction when selecting a view element
        during the recording of a scenario
        """
        self._viewclient.dump()
        root_tree_processed = process_nodes(
            self._viewclient.getRoot(),
            recording=True)
        selected_node_id = int(input("Which element do you want to click? "))
        (selected_dic, _, editText, selected_view) = \
            select_matching_node(root_tree_processed, selected_node_id)
        text_to_insert = None
        if editText:
            text_to_insert = input(
                "The pressed element allows the user to insert a "
                "text. Which text do you want to insert? ")
        print(
            "Clicking the selected view and waiting for "
            "it to load for two seconds")
        selected_view.touch()
        time.sleep(2)
        if text_to_insert is not None:
            print("Inserting text to the input field and"
                  " waiting for it to load for one seconds")
            # We don't need to store the text in this case as
            # the text will be stored together with the
            # details of the view object
            self.insert_text(recording=False,
                             parameters={"TEXT": text_to_insert})
            # self.get_device().type(text_to_insert)
            time.sleep(1)
            print("Pressing enter and waiting for "
                  "it to load for two seconds")
            self._device.press("KEYCODE_ENTER")
            time.sleep(2)
        yaml_converted_action = self.convert_view_action_to_yaml_output(
            selected_dic, text_to_insert)
        playbook_file_pointer = open(self.playbook_abs_file_path, "a")
        playbook_file_pointer.write(yaml_converted_action)
        playbook_file_pointer.close()
