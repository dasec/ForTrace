""" This module provides classes and functions for working with payload packages.

"""
from __future__ import absolute_import
__author__ = 'Sascha Kopp'

import zipfile
import six.moves.configparser
from enum import Enum
from os import path
import platform
import sys
import subprocess
from io import StringIO


class ExecutableTypes(Enum):
    """ Enumeration for payload executable formats.

    """
    PYTHON = 1
    NATIVE = 2
    OTHER = 3


class PayloadMetaData(object):
    """ Contains parsed information extracted from a config file.

    """

    def __init__(self, executable, executable_type, args):
        """ The constructor.

        :type args: str
        :type executable_type: int
        :type executable: str
        :param executable: the executable or script to be executed as payload
        :param executable_type: the type of executable
        :param args: additional command-line parameters
        """
        self.executable = executable
        self.executable_type = executable_type
        self.args = args


def load_and_unpack(filename, unpack_dir='./tmp/', password=None):
    """ Unpacks a payload.

    :type password: str
    :type unpack_dir: str
    :type filename: str
    :param filename: the file that contains the zipped payload
    :param unpack_dir: the directory where the content should be unpacked to
    :param password: the password of the zipped payload
    """
    z = zipfile.ZipFile(filename)
    z.extractall(unpack_dir, z.namelist(), password)


def parse_meta_data(filename='./tmp/meta.cfg'):
    """ Loads a file into memory and parses the content.

    :type filename: str
    :param filename: the file containing metadata
    :return: PayloadMetaData
    :raise: RuntimeError: Raised if either the Bot section and/or the executable entry is missing
    """
    cp = six.moves.configparser.ConfigParser()
    cp.read(filename)
    # executable = None
    # executable_type = None
    # args = None
    try:
        executable = cp.get('Bot', 'executable')
    except six.moves.configparser.NoSectionError:
        raise RuntimeError('Missing Bot section in config file')
    except six.moves.configparser.NoOptionError:
        raise RuntimeError('Missing executable entry')
    try:
        executable_type = cp.get('Bot', 'executable_type')
        if executable_type.upper() == 'PYTHON':
            executable_type = ExecutableTypes.PYTHON
        elif executable_type.upper() == 'NATIVE':
            executable_type = ExecutableTypes.NATIVE
        else:
            executable_type = ExecutableTypes.OTHER
    except six.moves.configparser.NoOptionError:
        executable_type = ExecutableTypes.PYTHON
    try:
        args = cp.get('Bot', 'args')
    except six.moves.configparser.NoOptionError:
        args = ''
    ret = PayloadMetaData(executable, executable_type, args)
    return ret


def execute_with_metadata(metadata, cwd='./tmp', use_default_python=True, python_executable='python.exe'):
    """ Executes a payload through metadata.


    :type python_executable: str
    :type use_default_python: bool
    :type cwd: str
    :rtype : subprocess.Popen
    :param use_default_python: use the python interpreter that launched this function
    :param python_executable: path to the python interpreter
    :type metadata: PayloadMetaData
    :param metadata: previously parsed metadata, needed to execute a bot instance
    :param cwd: the directory that should be used as execution root
    """
    if isinstance(metadata, PayloadMetaData):
        abs_cwd = path.abspath(cwd)
        abs_exec = path.abspath(abs_cwd + '/' + metadata.executable)
        python_bin = sys.executable
        if not use_default_python:
            python_bin = python_executable
        if metadata.executable_type == ExecutableTypes.PYTHON:
            if platform.system() == 'Windows':
                p = subprocess.Popen(python_bin + ' ' + abs_exec + ' ' + metadata.args, cwd=abs_cwd,
                                     creationflags=subprocess.CREATE_NEW_CONSOLE)
                return p
            else:
                p = subprocess.Popen(python_bin + ' ' + abs_exec + ' ' + metadata.args, cwd=abs_cwd, shell=True)
                return p
        elif metadata.executable_type == ExecutableTypes.NATIVE:
            if platform.system() == 'Windows':
                p = subprocess.Popen(abs_exec + ' ' + metadata.args, cwd=abs_cwd,
                                     creationflags=subprocess.CREATE_NEW_CONSOLE)
                return p
            else:
                p = subprocess.Popen(abs_exec + ' ' + metadata.args, cwd=abs_cwd, shell=True)
                return p
        elif metadata.executable_type == ExecutableTypes.OTHER:
            pass
        else:
            raise AssertionError('unreachable code reached')
    else:
        raise TypeError('metadata is not a PayloadMetaData-instance')


def generate_payload_from_single_file(path):
    # todo: test
    """ Packs a single script file into memory and generates a payload from it.

    :param path: path to file
    :return: memory buffer of zip file
    """
    zbuf = StringIO.StringIO()
    z = zipfile.ZipFile(zbuf, 'w')
    z.write(path, 'payload.py')
    meta = """[Bot]
executable=payload.py
executable_type=python
args=
    """
    z.writestr('meta.cfg', meta)
    z.close()
    zfile = zbuf.getvalue()
    zbuf.close()
    return zfile
