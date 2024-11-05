import yaml

PERFORM_LEFT_SWIPE_STR = "LEFT_SWIPE"
PERFORM_RIGHT_SWIPE_STR = "RIGHT_SWIPE"
PERFORM_TOP_SWIPE_STR = "TOP_SWIPE"
PERFORM_DOWN_SWIPE_STR = "DOWN_SWIPE"
PERFORM_LEFT_SWIPE_STR_LONG = "LEFT_SWIPE_LONG"
PERFORM_RIGHT_SWIPE_STR_LONG = "RIGHT_SWIPE_LONG"
PERFORM_TOP_SWIPE_STR_LONG = "TOP_SWIPE_LONG"
PERFORM_DOWN_SWIPE_STR_LONG = "DOWN_SWIPE_LONG"


class Gestures:
    """

    """

    def __init__(self,
                 device,
                 height,
                 width,
                 orientation,
                 playbook_file) -> None:
        self.device = device
        self.height = height
        self.width = width
        self.orientation = orientation
        self.playbook_file = playbook_file
        self.left_swipe_coordinates, \
            self.right_swipe_coordinates, \
            self.top_swipe_coordinates,\
            self.down_swipe_coordinates, \
            self.left_swipe_long_coordinates, \
            self.right_swipe_long_coordinates, \
            self.top_swipe_long_coordinates, \
            self.down_swipe_long_coordinates =\
            self.determine_swipe_coordinates()
        self.gestures = \
            {PERFORM_LEFT_SWIPE_STR: self.perform_left_swipe,
             PERFORM_RIGHT_SWIPE_STR: self.perform_left_swipe,
             PERFORM_TOP_SWIPE_STR: self.perform_left_swipe,
             PERFORM_DOWN_SWIPE_STR: self.perform_left_swipe,
             PERFORM_LEFT_SWIPE_STR_LONG: self.perform_left_swipe,
             PERFORM_RIGHT_SWIPE_STR_LONG: self.perform_right_swipe,
             PERFORM_TOP_SWIPE_STR_LONG: self.perform_top_swipe,
             PERFORM_DOWN_SWIPE_STR_LONG: self.perform_down_swipe}

    def determine_swipe_coordinates(self):
        # x1, y1, x2, y2
        # x1, y1 => Start of the swipe
        # x2, y2 => End of the swipe
        height = self.height
        width = self.width

        # x, y; top left coordinate is (0, 0)
        mid_left = width * 0.2, height / 2
        mid_right = width * 0.8, height / 2
        mid_down = width / 2, height * 0.8
        mid_top = width / 2, height * 0.2
        mid_center = width / 2, height / 2

        # Set coordinates
        # right to left
        left_swipe_coordinates = (mid_right, mid_center)
        # left to right
        right_swipe_coordinates = (mid_left, mid_center)
        # down to top
        top_swipe_coordinates = (mid_down, mid_center)
        # top to down
        down_swipe_coordinates = (mid_top, mid_center)
        left_swipe_long_coordinates = (mid_right, mid_left)
        right_swipe_long_coordinates = (mid_left, mid_right)
        top_swipe_long_coordinates = (mid_down, mid_top)
        down_swipe_long_coordinates = (mid_top, mid_down)
        return \
            left_swipe_coordinates, \
            right_swipe_coordinates, \
            top_swipe_coordinates, \
            down_swipe_coordinates, \
            left_swipe_long_coordinates, \
            right_swipe_long_coordinates, \
            top_swipe_long_coordinates, \
            down_swipe_long_coordinates

    def perform_left_swipe(self, duration=1000):
        x1_y1, x2_y2 = self.left_swipe_coordinates[0], \
            self.left_swipe_coordinates[1]
        self.device().drag(x1_y1, x2_y2, duration)

    def perform_right_swipe(self, duration=1000):
        x1_y1, x2_y2 = self.right_swipe_coordinates[0], \
            self.right_swipe_coordinates[1]
        self.device().drag(x1_y1, x2_y2, duration)

    def perform_down_swipe(self, duration=1000):
        x1_y1, x2_y2 = self.down_swipe_coordinates[0], \
            self.down_swipe_coordinates[1]
        self.device().drag(x1_y1, x2_y2, duration)

    def perform_top_swipe(self, duration=1000):
        x1_y1, x2_y2 = self.top_swipe_coordinates[0], \
            self.top_swipe_coordinates[1]
        self.device().drag(x1_y1, x2_y2, duration)

    @staticmethod
    def dump_gesture(yaml_file, action_id, gesture_string):
        yaml_file.write(yaml.dump({
            action_id: {
                "TYPE": "GESTURES",
                "SUBTYPE": gesture_string}}))

    def replay_gesture(self, subtype_of_action):
        self.gestures.get(subtype_of_action)()
        return True, None

    def record_perform_gesture(self, playbook_id):
        # Build temporary connection between the
        # enumeration and the corresponding gestures
        tmp_dict = {}
        gesture_id = 0
        for gesture_id, (gesture_string, gesture) in enumerate(
                self.gestures.items()):
            print("{}: {}".format(gesture_id, gesture_string))
            tmp_dict[gesture_id] = {gesture_string: gesture}
        selection = int(
            input("Which gesture do you want to perform? ")
        )
        if selection > gesture_id:
            print("Number not within the range")
        else:
            try:
                gesture_string, gesture = tmp_dict[selection].popitem()
                print("Performing {}".format(gesture_string))
                gesture()
                # We do NOT store the coordinates of the swipe
                # as the coordinates depend on the display size
                # and thus can change
                self.dump_gesture(
                    self.playbook_file,
                    playbook_id,
                    gesture_string
                )
            except Exception as e:
                print(e)