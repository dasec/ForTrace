from __future__ import absolute_import
import os
from itertools import chain
from six.moves import range


def file_exists(path):
    return os.path.isfile(path)


def parse_attachment_string(attachment_path_list):
    if attachment_path_list is None:
        return None

    if len(attachment_path_list) > 1:
        return create_comma_separated_string_for_multiple_paths(attachment_path_list)

    elif len(attachment_path_list) == 1:
        return attachment_path_list[0]

    return None


def create_comma_separated_string_for_multiple_paths(attachment_path_list):
    attachment_string = ""
    for path in attachment_path_list[:-1]:
        attachment_string += path + ','
    return attachment_string + attachment_path_list[-1]


def copy_file_to_shared_file_system(path):
    pass


def escape_password_string(password):
    escaped_password_string = ""
    for char in password:
        if char_is_special_character(char):
            escaped_password_string += "{" + char + "}"
        else:
            escaped_password_string += char
    return escaped_password_string


def char_is_special_character(char):
    # Checks if the char is a special character by comparing the ASCII code
    # For more details see:
    # https://www.ionos.com/digitalguide/server/know-how/ascii-codes-overview-of-all-characters-on-the-ascii-table/
    return ord(char) in chain(list(range(32, 48)), list(range(58,65)), list(range(91, 97)), list(range(123, 127)))
