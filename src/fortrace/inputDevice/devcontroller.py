# coding=utf-8
""" Contains a client and server for manipulating virtual input devices.
    This module is divided into the following class types.
    Adapters provide the interfaces to drivers or user-space applications.
    Translators provide character to scan-code translations.
    The server runs on a guest and receives control messages.
    The client connects to the server and send control messages.

"""
from __future__ import absolute_import
import six.moves.configparser
import binascii
import six.moves.cPickle
import json
import platform
import socket

# from enum import Enum
import struct
from enum import IntEnum
from abc import ABCMeta, abstractmethod
from fortrace.core.guest import Guest
from fortrace.botnet.common.loggerbase import LoggerBase
from fortrace.botnet.common.runtimequery import RuntimeQuery
from fortrace.botnet.common.threadmanager import ThreadManager
from fortrace.botnet.net.meta.tcpclientbase import TcpClientBase
from fortrace.botnet.net.meta.tcpserverbase import TcpServerBase
from fortrace.botnet.net.netutility import NetUtility
import six
from six import unichr
from six.moves import range

try:
    import win32api
    import win32file

    dev_controller_win_api_available = True
except ImportError:
    dev_controller_win_api_available = False

# class SpecialAndFunctionKeys(Enum):
#    """ This class contains all special and function keys that can't be expressed as a single character.
#        Escaped key sequences are also included.
#
#    """
#    ESC = 0
#    F1 = 1
#    F2 = 2
#    F3 = 3
#    F4 = 4
#    F5 = 5
#    F6 = 6
#    F7 = 7
#    F8 = 8
#    F9 = 9
#    F10 = 10
#    F11 = 11
#    F12 = 12
#    TAB = 13
#    ENTER = 14
#    BS = 15
#    PAUSE = 16
#    BREAK = 17
#    PRINT = 18
#    SYSRQ = 19
#    DEL = 20
#    INSERT = 21
#    HOME = 22
#    PGUP = 23
#    PGDOWN = 24

SpecialAndFunctionKeys = ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'TAB',
                          'ENTER', 'SPACE', 'BACKSPACE', 'PAUSE', 'BREAK', 'PRINT', 'SYSRQ', 'DEL', 'INSERT', 'HOME',
                          'PAGEUP', 'PAGEDOWN', 'ARROWLEFT', 'ARROWRIGHT', 'ARROWUP', 'ARROWDOWN']


class UsbVMultiShiftKeys(IntEnum):
    """ A class representing shift key values for the usb translator.

    """
    LCTRL = 0x01
    LSHIFT = 0x02
    LALT = 0x04
    LGUI = 0x08
    RCTRL = 0x10
    RSHIFT = 0x20
    RALT = 0x40
    RGUI = 0x80


DEV_PORT = 10999


def _unicode_to_str(data):
    """ Utility function to make json encoded data an ascii string
        Original taken from:
        http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python

    :param data: either a dict, list or unicode string
    :return: ascii data
    """
    if isinstance(data, dict):
        return {_unicode_to_str(key): _unicode_to_str(value) for key, value in six.iteritems(data)}
    elif isinstance(data, list):
        return [_unicode_to_str(element) for element in data]
    elif isinstance(data, six.text_type):
        return data.encode('utf-8')
    else:
        return data


class ILayoutSwitcher(six.with_metaclass(ABCMeta, object)):
    @abstractmethod
    def switch_layout(self, keymap):
        """

        :type keymap: str
        :param keymap: the name of the keymap, ex. de, en, etc.
        """
        raise NotImplementedError()


class IKeyboardMethods(six.with_metaclass(ABCMeta, object)):
    @abstractmethod
    def kb_write_text(self, text):
        raise NotImplementedError()

    @abstractmethod
    def kb_write_special_key(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        raise NotImplementedError()

    @abstractmethod
    def kb_write_scancode(self, scan_codes):
        raise NotImplementedError()


class IRelativeMouseMethods(six.with_metaclass(ABCMeta, object)):
    @abstractmethod
    def mouse_move_relative(self, x, y):
        raise NotImplementedError()

    @abstractmethod
    def mouse_click(self, left):
        raise NotImplementedError()

    @abstractmethod
    def mouse_double_click(self, left):
        raise NotImplementedError()

    @abstractmethod
    def mouse_hold(self, left):
        raise NotImplementedError()

    @abstractmethod
    def mouse_release(self, left):
        raise NotImplementedError()


class IAbsoluteMouseMethods(object):
    pass


class DevDriverAdapter(six.with_metaclass(ABCMeta, IKeyboardMethods, IRelativeMouseMethods)):
    @abstractmethod
    def kb_write_text(self, text):
        raise NotImplementedError()

    @abstractmethod
    def kb_write_scancode(self, scan_codes):
        raise NotImplementedError()

    @abstractmethod
    def kb_write_special_key(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        raise NotImplementedError()

    @abstractmethod
    def mouse_move_relative(self, x, y):
        raise NotImplementedError()

    @abstractmethod
    def mouse_click(self, left):
        raise NotImplementedError()

    def mouse_double_click(self, left):
        self.mouse_click(left)
        self.mouse_click(left)

    @abstractmethod
    def mouse_hold(self, left):
        raise NotImplementedError()

    @abstractmethod
    def mouse_release(self, left):
        raise NotImplementedError()

    @abstractmethod
    def write_to_kb_dev(self, data):
        raise NotImplementedError()

    @abstractmethod
    def write_to_mouse_dev(self, data):
        raise NotImplementedError()


class DummyDriverAdapter(DevDriverAdapter, LoggerBase):
    def __init__(self):
        LoggerBase.__init__(self, 'DummyDriverAdapter')
        self.logger.debug('Using the DummyDriverAdapter')
        self.translator = DummyTranslator()

    def write_to_mouse_dev(self, data):
        pass

    def mouse_move_relative(self, x, y):
        self.logger.debug("event: mouse move relative - x:%d y:%d", x, y)

    def kb_write_scancode(self, scan_codes):
        self.logger.debug("event: kb write scancode")

    def mouse_hold(self, left):
        self.logger.debug("event: mouse hold - left: %s", str(left))

    def mouse_click(self, left):
        self.logger.debug("event: mouse click - left: %s", str(left))

    def write_to_kb_dev(self, data):
        pass

    def mouse_release(self, left):
        self.logger.debug("event: mouse release - left: %s", str(left))

    def kb_write_text(self, text):
        self.logger.debug("event: kb write text - text: %s", text)

    def kb_write_special_key(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        self.logger.debug(
            "event: kb write special key - lctrl: %s lalt: %s lshift: %s ralt: %s lgui: %s rgui: %s key: %s",
            str(lctrl), str(lalt), str(lshift), str(ralt), str(lgui), str(rgui), key)


class LinuxAbstractAdapter(six.with_metaclass(ABCMeta, DevDriverAdapter)):
    def __init__(self):
        #  if not os.path.isfile('/dev/vkbd'):
        #     raise RuntimeError('Could not find keyboard device')
        # if not os.path.isfile('/dev/vsermouse'):
        #     raise RuntimeError('Could not find mouse device')
        try:
            self.devkb = open('/dev/vkbd', 'w+b')
            self.devmouse = open('/dev/vsermouse', 'w+b')
        except OSError:
            raise RuntimeError('Could not open device drivers')

    @abstractmethod
    def kb_write_text(self, text):
        raise NotImplementedError()

    @abstractmethod
    def kb_write_special_key(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        raise NotImplementedError()

    @abstractmethod
    def kb_write_scancode(self, scan_codes):
        raise NotImplementedError()

    def mouse_release(self, left):
        b = bytearray()
        # todo: handle separate release events
        if left:
            b.append(0x87)
            b.append(0x00)
            b.append(0x00)
            b.append(0x00)
            b.append(0x00)
        else:
            b.append(0x87)
            b.append(0x00)
            b.append(0x00)
            b.append(0x00)
            b.append(0x00)
        self.write_to_mouse_dev(b)

    def mouse_move_relative(self, x, y):
        b = bytearray()
        b.append(0x87)  # todo: handle state changes for drag-and-drop, for now all keys will be released
        b.append(x)
        b.append(y)
        b.append(0x00)
        b.append(0x00)
        self.write_to_mouse_dev(b)

    def mouse_click(self, left):
        self.mouse_hold(left)
        self.mouse_release(left)

    def mouse_hold(self, left):
        b = bytearray()
        # todo: handle separate hold events
        if left:
            b.append(0x83)
            b.append(0x00)
            b.append(0x00)
            b.append(0x00)
            b.append(0x00)
        else:
            b.append(0x86)
            b.append(0x00)
            b.append(0x00)
            b.append(0x00)
            b.append(0x00)
        self.write_to_mouse_dev(b)

    def write_to_kb_dev(self, data):
        self.devkb.write(data)
        self.devkb.flush()

    def write_to_mouse_dev(self, data):
        self.devmouse.write(data)
        self.devmouse.flush()


# class LinuxConsoleAdapter(LinuxAbstractAdapter, LoggerBase):
#    """ An adapter for the linux console with linux drivers.
#
#    """
#
#    def __init__(self):
#        LinuxAbstractAdapter.__init__(self)
#        LoggerBase.__init__(self, 'LinuxConsoleAdapter')
#        self.logger.debug('Using the LinuxConsoleAdapter')
#        self.translator = XtTranslator()
#        self.translator.load_template('/etc/fortrace/set1-basic.conf')
#        self.translator.generate_mapping()
#
#    def write_to_mouse_dev(self, data):
#        LinuxAbstractAdapter.write_to_mouse_dev(self, data)
#
#    def write_to_kb_dev(self, data):
#        LinuxAbstractAdapter.write_to_kb_dev(self, data)
#
#    def mouse_hold(self, left):
#        LinuxAbstractAdapter.mouse_hold(self, left)
#
#    def mouse_move_relative(self, x, y):
#        LinuxAbstractAdapter.mouse_move_relative(self, x, y)
#
#    def mouse_click(self, left):
#        LinuxAbstractAdapter.mouse_click(self, left)
#
#    def mouse_release(self, left):
#        LinuxAbstractAdapter.mouse_release(self, left)
#
#    def kb_write_scancode(self, scan_codes):
#        self.write_to_kb_dev(scan_codes)
#
#    def kb_write_text(self, text):
#        self.logger.debug('writing text to kbdev: %s', text)
#        try:
#            b = self.translator.build_scancodes_from_string(text)
#        except KeyError:
#            self.logger.error('one or more keys not found in mapper')
#            return
#        self.logger.debug('writing byte sequence to kbdev: %s', binascii.hexlify(b))
#        self.write_to_kb_dev(b)
#
#    def kb_write_special_key(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
#        try:
#            b = self.translator.build_special_key_sequence(lctrl, lalt, lshift, ralt, lgui, rgui, key)
#        except KeyError:
#            self.logger.error('bad key')
#            return
#        self.logger.debug('writing byte sequence to kbdev: %s', binascii.hexlify(b))
#        self.write_to_kb_dev(b)


class LinuxXServerAdapter(LinuxAbstractAdapter, ILayoutSwitcher, LoggerBase):
    """ Driver-Adapter for the virtual-device-drivers in the package top-tree.

    """

    def __init__(self):
        LinuxAbstractAdapter.__init__(self)
        LoggerBase.__init__(self, 'LinuxXServerAdapter')
        self.logger.debug('Using the LinuxXServerAdapter')
        self.translator = XTLayoutTranslator()
        self.translator.load_template("/etc/fortrace/set1-de.conf")
        self.translator.generate_mapping()
        # self.logger.debug('Set layout to <de>')

    def switch_layout(self, keymap):
        self.translator = XTLayoutTranslator()
        self.translator.load_template(keymap)
        self.translator.generate_mapping()

    def write_to_mouse_dev(self, data):
        LinuxAbstractAdapter.write_to_mouse_dev(self, data)

    def write_to_kb_dev(self, data):
        LinuxAbstractAdapter.write_to_kb_dev(self, data)

    def mouse_hold(self, left):
        LinuxAbstractAdapter.mouse_hold(self, left)

    def mouse_move_relative(self, x, y):
        LinuxAbstractAdapter.mouse_move_relative(self, x, y)

    def mouse_click(self, left):
        LinuxAbstractAdapter.mouse_click(self, left)

    def mouse_release(self, left):
        LinuxAbstractAdapter.mouse_release(self, left)

    def kb_write_scancode(self, scan_codes):
        self.write_to_kb_dev(scan_codes)

    def kb_write_text(self, text):
        self.logger.debug('writing text to kbdev: %s', text)
        ords = []
        for s in text:
            ords.append(ord(s))
        self.logger.debug('corresponds to: %s', str(ords))
        try:
            b = self.translator.build_scancodes_from_string(text)
        except KeyError:
            self.logger.error('one or more keys not found in mapper')
            return
        self.logger.debug('writing byte sequence to kbdev: %s', binascii.hexlify(b))
        self.write_to_kb_dev(b)

    def kb_write_special_key(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        try:
            b = self.translator.build_special_key_sequence(lctrl, lalt, lshift, ralt, lgui, rgui, key)
        except KeyError:
            self.logger.error('bad key')
            return
        self.logger.debug('writing byte sequence to kbdev: %s', binascii.hexlify(b))
        self.write_to_kb_dev(b)


class WindowsAdapter(DevDriverAdapter, LoggerBase):
    """ Driver-Adapter for the vmulti-virtual-hid-device-driver.
        Note: All communication is done via 16 byte data packets to the helper application.

    """

    def __init__(self):
        LoggerBase.__init__(self, 'WindowsAdapter')
        self.logger.debug('Using the WindowsAdapter')
        if not dev_controller_win_api_available:
            self.logger.error('Win32api module missing!')
            raise RuntimeError('Win32api module missing!')
        self.translator = UsbTranslator()
        self.translator.load_template("C:/usb-de.conf")
        self.translator.generate_mapping()
        self.pipe = win32file.CreateFile('\\\\.\\pipe\\vmultidev', win32file.GENERIC_WRITE, win32file.FILE_SHARE_READ,
                                         None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, None)
        # self.logger.debug('Set layout to <de>')

    def __del__(self):
        win32api.CloseHandle(self.pipe)

    def kb_write_text(self, text):
        self.logger.debug('writing text to kbdev: %s', text)
        ords = []
        for s in text:
            ords.append(ord(s))
        self.logger.debug('corresponds to: %s', str(ords))
        try:
            b = self.translator.build_scancodes_from_string(text)
        except KeyError:
            self.logger.error('one or more keys not found in mapper')
            return
        self.logger.debug('writing byte sequence to kbdev: %s', binascii.hexlify(b))
        self.write_to_kb_dev(b)

    def mouse_hold(self, left):
        b = bytearray()
        b.append(0x02)  # rela-mouse-id
        if left:
            b.append(0x01)  # mouse-1
        else:
            b.append(0x02)  # mouse-2
        b.append(0x00)  # x
        b.append(0x00)  # y
        b.append(0x00)  # wheel
        for x in range(11):  # dummy data
            b.append(0x00)
        self.write_to_mouse_dev(b)

    def mouse_click(self, left):
        b = bytearray()
        b.append(0x02)  # rela-mouse-id
        if left:
            b.append(0x01)  # mouse-1
        else:
            b.append(0x02)  # mouse-2
        b.append(0x00)  # x
        b.append(0x00)  # y
        b.append(0x00)  # wheel
        for x in range(11):  # dummy data
            b.append(0x00)
        b.append(0x02)  # rela-mouse-id
        b.append(0x00)  # no mouse button
        b.append(0x00)  # x
        b.append(0x00)  # y
        b.append(0x00)  # wheel
        for x in range(11):  # dummy data
            b.append(0x00)
        self.write_to_mouse_dev(b)

    def mouse_release(self, left):
        b = bytearray()
        b.append(0x02)  # rela-mouse-id
        b.append(0x00)  # no mouse button
        b.append(0x00)  # x
        b.append(0x00)  # y
        b.append(0x00)  # wheel
        for x in range(11):  # dummy data
            b.append(0x00)
        self.write_to_mouse_dev(b)

    def mouse_move_relative(self, x, y):
        b = bytearray()
        b.append(0x02)  # rela-mouse-id
        b.append(0x00)  # no mouse button
        b.append(x)  # x
        b.append(y)  # y
        b.append(0x00)  # wheel
        for x in range(11):  # dummy data
            b.append(0x00)
        self.write_to_mouse_dev(b)

    def write_to_kb_dev(self, data):
        assert (len(data) % 16) == 0
        win32file.WriteFile(self.pipe, data, None)

    def kb_write_scancode(self, scan_codes):
        self.write_to_kb_dev(scan_codes)

    def kb_write_special_key(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        try:
            b = self.translator.build_special_key_sequence(lctrl, lalt, lshift, ralt, lgui, rgui, key)
        except KeyError:
            self.logger.error('bad key')
            return
        self.logger.debug('writing byte sequence to kbdev: %s', binascii.hexlify(b))
        self.write_to_kb_dev(b)

    def write_to_mouse_dev(self, data):
        assert (len(data) % 16) == 0
        win32file.WriteFile(self.pipe, data, None)


class MacOSXAdapter:
    def __init__(self):
        raise NotImplementedError()


class DevTranslator(six.with_metaclass(ABCMeta, object)):
    def __init__(self):
        self.mapper = dict()
        self.raws = dict()
        self.overrides = dict()
        # only for xt and at input
        self.begseq = bytearray()
        self.endseq = bytearray()
        # SPACE
        self.mapper[' '] = bytearray()
        # escapes
        self.mapper['\a'] = bytearray()  # UNMAPPED
        self.mapper['\b'] = bytearray()  # BACKSPACE|UNMAPPED
        self.mapper['\f'] = bytearray()  # UNMAPPED
        self.mapper['\n'] = bytearray()  # ENTER
        self.mapper['\r'] = bytearray()  # HOME
        self.mapper['\t'] = bytearray()  # TAB
        self.mapper['\v'] = bytearray()  # UNMAPPED
        # numkeys
        self.mapper['1'] = bytearray()
        self.mapper['2'] = bytearray()
        self.mapper['3'] = bytearray()
        self.mapper['4'] = bytearray()
        self.mapper['5'] = bytearray()
        self.mapper['6'] = bytearray()
        self.mapper['7'] = bytearray()
        self.mapper['8'] = bytearray()
        self.mapper['9'] = bytearray()
        self.mapper['0'] = bytearray()

    @staticmethod
    def _raw_to_byte_array(raw):
        if raw == '':
            return bytearray()
        else:
            x = raw[1:-1]
            c = str()
            s = x.split(',')
            for v in s:
                c += v[2:]
            ret_val = bytearray.fromhex(c)
            return ret_val

    def load_template(self, filename):
        p = six.moves.configparser.RawConfigParser()
        p.read(filename)
        # self.raws['BEG'] = p.get('config', 'BEG')
        # self.raws['END'] = p.get('config', 'END')
        self.raws[' '] = p.get('config', 'SPACE')
        self.raws['\a'] = p.get('config', r'\a')
        self.raws['\b'] = p.get('config', r'\b')
        self.raws['\f'] = p.get('config', r'\f')
        self.raws['\n'] = p.get('config', r'\n')
        self.raws['\r'] = p.get('config', r'\r')
        self.raws['\t'] = p.get('config', r'\t')
        self.raws['\v'] = p.get('config', r'\v')
        self.raws['1'] = p.get('config', '1')
        self.raws['2'] = p.get('config', '2')
        self.raws['3'] = p.get('config', '3')
        self.raws['4'] = p.get('config', '4')
        self.raws['5'] = p.get('config', '5')
        self.raws['6'] = p.get('config', '6')
        self.raws['7'] = p.get('config', '7')
        self.raws['8'] = p.get('config', '8')
        self.raws['9'] = p.get('config', '9')
        self.raws['0'] = p.get('config', '0')
        self.raws['k1'] = p.get('config', 'k1')
        self.raws['k2'] = p.get('config', 'k2')
        self.raws['k3'] = p.get('config', 'k3')
        self.raws['k4'] = p.get('config', 'k4')
        self.raws['k5'] = p.get('config', 'k5')
        self.raws['k6'] = p.get('config', 'k6')
        self.raws['k7'] = p.get('config', 'k7')
        self.raws['k8'] = p.get('config', 'k8')
        self.raws['k9'] = p.get('config', 'k9')
        self.raws['k0'] = p.get('config', 'k0')
        for k, v in six.iteritems(self.raws):
            self.overrides[k] = self._raw_to_byte_array(v)

    @abstractmethod
    def generate_mapping(self):
        raise NotImplementedError()

    @abstractmethod
    def build_scancodes_from_string(self, text):
        raise NotImplementedError()

    @abstractmethod
    def build_special_key_sequence(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        raise NotImplementedError()


class DummyTranslator(DevTranslator):
    def __init__(self):
        DevTranslator.__init__(self)

    def load_template(self, filename):
        pass

    def generate_mapping(self):
        pass

    def build_scancodes_from_string(self, text):
        pass

    def build_special_key_sequence(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        pass


# class XtTranslator(DevTranslator):
#    """ A basic char to scancode translator for the linux-console using set1 codes.
#
#    """
#
#    def __init__(self):
#        DevTranslator.__init__(self)
#
#    def generate_mapping(self):
#        # write ascii input method
#        for x in range(0, 256):
#            c = bytearray()
#            c += self.overrides['BEG']
#            s = str(x)
#            for z in s:
#                c += self.overrides['k' + z]
#            c += self.overrides['END']
#            self.mapper[chr(x)] = c
#        # overwrite with original overrides
#        for k, v in self.overrides.iteritems():
#            if len(k) == 1:
#                self.mapper[k] = v
#
#    def build_scancodes_from_string(self, text):
#        b = bytearray()
#        for c in text:
#            b += self.mapper[c]
#        return b
#
#    def build_special_key_sequence(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
#        b = bytearray()
#        # todo: implement
#        return b


class XTLayoutTranslator(DevTranslator):
    def __init__(self):
        DevTranslator.__init__(self)

    def load_template(self, keymap_file="/etc/fortrace/set1-de.conf"):
        """Load a language specific template

        :type keymap_file: str
        :param keymap_file: corresponds to a keymap_file, for example de,en,etc. (for now only de is supported)
        """
        p = six.moves.configparser.RawConfigParser()
        p.optionxform = str  # needs to be set on windows for case-sensitivity, anyway set it for linux too
        p.read(keymap_file)
        for k, v in p.items('config'):
            self.raws[k] = v
        # key sequences for shift keys
        self.raws[u'LCTRLBEG'] = p.get('config', 'LCTRLBEG')
        self.raws[u'LCTRLEND'] = p.get('config', 'LCTRLEND')
        self.raws[u'LSHIFTBEG'] = p.get('config', 'LSHIFTBEG')
        self.raws[u'LSHIFTEND'] = p.get('config', 'LSHIFTEND')
        self.raws[u'LALTBEG'] = p.get('config', 'LALTBEG')
        self.raws[u'LALTEND'] = p.get('config', 'LALTEND')
        self.raws[u'LGUIBEG'] = p.get('config', 'LGUIBEG')
        self.raws[u'LGUIEND'] = p.get('config', 'LGUIEND')
        self.raws[u'RGUIBEG'] = p.get('config', 'RGUIBEG')
        self.raws[u'RGUIEND'] = p.get('config', 'RGUIEND')
        self.raws[u'RALTBEG'] = p.get('config', 'RALTBEG')
        self.raws[u'RALTEND'] = p.get('config', 'RALTEND')
        # special and function keys
        self.raws[u'ESC'] = p.get('config', 'ESC')
        self.raws[u'TAB'] = p.get('config', 'TAB')
        self.raws[u'ENTER'] = p.get('config', 'ENTER')
        self.raws[u'BACKSPACE'] = p.get('config', 'BACKSPACE')
        self.raws[u'INSERT'] = p.get('config', 'INSERT')
        self.raws[u'HOME'] = p.get('config', 'HOME')
        self.raws[u'DEL'] = p.get('config', 'DEL')
        self.raws[u'END'] = p.get('config', 'END')
        self.raws[u'PAGEUP'] = p.get('config', 'PAGEUP')
        self.raws[u'PAGEDOWN'] = p.get('config', 'PAGEDOWN')
        self.raws[u'PRINT'] = p.get('config', 'PRINT')
        self.raws[u'SYSRQ'] = p.get('config', 'SYSRQ')
        self.raws[u'PAUSE'] = p.get('config', 'PAUSE')
        self.raws[u'BREAK'] = p.get('config', 'BREAK')
        self.raws[u'F1'] = p.get('config', 'F1')
        self.raws[u'F2'] = p.get('config', 'F2')
        self.raws[u'F3'] = p.get('config', 'F3')
        self.raws[u'F4'] = p.get('config', 'F4')
        self.raws[u'F5'] = p.get('config', 'F5')
        self.raws[u'F6'] = p.get('config', 'F6')
        self.raws[u'F7'] = p.get('config', 'F7')
        self.raws[u'F8'] = p.get('config', 'F8')
        self.raws[u'F9'] = p.get('config', 'F9')
        self.raws[u'F10'] = p.get('config', 'F10')
        self.raws[u'F11'] = p.get('config', 'F11')
        self.raws[u'F12'] = p.get('config', 'F12')
        self.raws[u'ARROWLEFT'] = p.get('config', 'ARROWLEFT')
        self.raws[u'ARROWRIGHT'] = p.get('config', 'ARROWRIGHT')
        self.raws[u'ARROWUP'] = p.get('config', 'ARROWUP')
        self.raws[u'ARROWDOWN'] = p.get('config', 'ARROWDOWN')
        # non-single character keys
        self.raws[u' '] = p.get('config', 'SPACE')
        self.raws[u'\a'] = p.get('config', r'\a')
        self.raws[u'\b'] = p.get('config', r'\b')
        self.raws[u'\f'] = p.get('config', r'\f')
        self.raws[u'\n'] = p.get('config', r'\n')
        self.raws[u'\r'] = p.get('config', r'\r')
        self.raws[u'\t'] = p.get('config', r'\t')
        self.raws[u'\v'] = p.get('config', r'\v')
        # special cases conflicting with the parser
        self.raws[u'#'] = p.get('config', 'HASH')
        self.raws[u'='] = p.get('config', 'EQUAL')
        self.raws[u':'] = p.get('config', 'COLON')
        self.raws[u';'] = p.get('config', 'SEMICOLON')
        # extended sign characters
        self.raws[u'°'] = p.get('config', 'DEGREE')
        self.raws[u'€'] = p.get('config', 'EURO')
        self.raws[u'§'] = p.get('config', 'PARAGRAPH')
        self.raws[u'²'] = p.get('config', 'SMALL2')
        self.raws[u'³'] = p.get('config', 'SMALL3')
        self.raws[u'´'] = p.get('config', 'AKZENT')
        # language specific
        self.raws[u'ß'] = p.get('config', 'DESZ')
        self.raws[u'Ä'] = p.get('config', 'DEUMLUA')
        self.raws[u'ä'] = p.get('config', 'DEUMLLA')
        self.raws[u'Ö'] = p.get('config', 'DEUMLUO')
        self.raws[u'ö'] = p.get('config', 'DEUMLLO')
        self.raws[u'Ü'] = p.get('config', 'DEUMLUU')
        self.raws[u'ü'] = p.get('config', 'DEUMLLU')
        for k, v in six.iteritems(self.raws):
            self.overrides[k] = self._raw_to_byte_array(v)

    def generate_mapping(self):
        # initialize all unknown chars as empty sequences
        """ Generates the ascii-to-scancode-map

        """
        for x in range(0, 256):
            self.mapper[unichr(x)] = bytearray()
        for k, v in six.iteritems(self.overrides):
            if len(k) == 1:
                self.mapper[k] = v

    def build_scancodes_from_string(self, text):
        b = bytearray()
        for c in text:
            b += self.mapper[c]
        return b

    def _get_special_key_scancode_sequence(self, key, side_key=None):
        """ Returns the representing bytes for a specified key.
            Only used for keys specified in SpecialAndFunctionKeys.

        :type key: str
        :type side_key: None | str
        :param key: a value from SpecialAndFunctionKeys list
        :param side_key: a secondary key used in conjunction with for example sysrq (future work)
        :return: the sequence of bytes for the specified key
        :rtype: bytearray
        """
        # b = bytearray()
        # b = self.overrides[key]
        # return b
        return self.overrides[key]

    def build_special_key_sequence(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        """ Generates a byte sequence for special and function key presses.

        :type lctrl: bool
        :type lalt: bool
        :type lshift: bool
        :type ralt: bool
        :type lgui: bool
        :type rgui: bool
        :type key: str
        :param lctrl: the left control key
        :param lalt: the left alt key
        :param lshift: the left shift key
        :param ralt: the right alt key
        :param lgui: the left gui key
        :param rgui: the right gui key
        :param key: a single key character or a value from SpecialAndFunctionKeys
        :return: a sequence of bytes representing the pressed key(s)
        :rtype: bytearray
        """
        bbeg = bytearray()
        bend = bytearray()
        if len(key) > 1:
            bmid = self._get_special_key_scancode_sequence(key)
        else:
            bmid = self.build_scancodes_from_string(key)
        if lctrl:
            bbeg += self.overrides[u'LCTRLBEG']
        if lalt:
            bbeg += self.overrides[u'LALTBEG']
        if lshift:
            bbeg += self.overrides[u'LSHIFTBEG']
        if ralt:
            bbeg += self.overrides[u'RALTBEG']
        if lgui:
            bbeg += self.overrides[u'LGUIBEG']
        if rgui:
            bbeg += self.overrides[u'RGUIBEG']
            bend += self.overrides[u'RGUIEND']
        if lgui:
            bend += self.overrides[u'LGUIEND']
        if ralt:
            bend += self.overrides[u'RALTEND']
        if lshift:
            bend += self.overrides[u'LSHIFTEND']
        if lalt:
            bend += self.overrides[u'LALTEND']
        if lctrl:
            bend += self.overrides[u'LCTRLEND']
        return bbeg + bmid + bend


class UsbTranslator(DevTranslator):
    def __init__(self):
        DevTranslator.__init__(self)

    def build_scancodes_from_string(self, text):
        b = bytearray()
        for c in text:
            x = len(self.mapper[c])
            if x != 0:
                b.append(0x01)
                b += self.mapper[c]
                x = 7 - x
                for _ in range(x):  # fill-bytes
                    b.append(0x00)
                for _ in range(8):  # dummy-data to reach 16 byte boundary
                    b.append(0x00)
                b.append(0x01)  # cancel keypress, maybe move this to the config file
                for _ in range(15):  # fill with zeros for release event
                    b.append(0x00)
        return b

    def _get_special_key_scancode_sequence(self, key, side_key=None):
        """ Returns the representing bytes for a specified key.
            Only used for keys specified in SpecialAndFunctionKeys.

        :type key: str
        :type side_key: None | str
        :param key: a value from SpecialAndFunctionKeys list
        :param side_key: a secondary key used in conjunction with for example sysrq (future work)
        :return: the sequence of bytes for the specified key
        :rtype: bytearray
        """
        b = bytearray()
        x = len(self.overrides[key])
        if x != 0:
            b.append(0x01)
            b += self.overrides[key]
            x = 7 - x
            for _ in range(x):  # fill-bytes
                b.append(0x00)
            for _ in range(8):  # dummy-data to reach 16 byte boundary
                b.append(0x00)
            b.append(0x01)  # cancel keypress, maybe move this to the config file
            for _ in range(15):  # fill with zeros for release event
                b.append(0x00)
        return b

    def build_special_key_sequence(self, lctrl, lalt, lshift, ralt, lgui, rgui, key):
        """ Generates a byte sequence for special and function key presses.

        :type lctrl: bool
        :type lalt: bool
        :type lshift: bool
        :type ralt: bool
        :type lgui: bool
        :type rgui: bool
        :type key: str
        :param lctrl: the left control key
        :param lalt: the left alt key
        :param lshift: the left shift key
        :param ralt: the right alt key
        :param lgui: the left gui key
        :param rgui: the right gui key
        :param key: a single key character or a value from SpecialAndFunctionKeys
        :return: a sequence of bytes representing the pressed key(s)
        :rtype: bytearray
        """
        if len(key) == 1:
            b = self.build_scancodes_from_string(key)
        else:
            b = self._get_special_key_scancode_sequence(key)
        if lctrl:
            b[1] |= UsbVMultiShiftKeys.LCTRL
        if lalt:
            b[1] |= UsbVMultiShiftKeys.LALT
        if lshift:
            b[1] |= UsbVMultiShiftKeys.LSHIFT
        if ralt:
            b[1] |= UsbVMultiShiftKeys.RALT
        if lgui:
            b[1] |= UsbVMultiShiftKeys.LGUI
        return b

    def generate_mapping(self):
        # initialize all unknown chars as empty sequences
        """ Generates the ascii-to-scancode-map

        """
        for x in range(0, 256):
            self.mapper[unichr(x)] = bytearray()
        for k, v in six.iteritems(self.overrides):
            if len(k) == 1:
                self.mapper[k] = v

    def load_template(self, keymap_file="C:/usb-de.conf"):
        """Load a language specific template

        :type keymap_file: str
        :param keymap_file: corresponds to a keymap, for example de,en,etc. (for now only de is supported)
        """
        p = six.moves.configparser.RawConfigParser()
        p.optionxform = str  # needs to be set on windows for case-sensitivity
        p.read(keymap_file)
        for k, v in p.items('config'):
            self.raws[k] = v
        # special and function keys
        self.raws[u'ESC'] = p.get('config', 'ESC')
        self.raws[u'TAB'] = p.get('config', 'TAB')
        self.raws[u'ENTER'] = p.get('config', 'ENTER')
        self.raws[u'BACKSPACE'] = p.get('config', 'BACKSPACE')
        self.raws[u'INSERT'] = p.get('config', 'INSERT')
        self.raws[u'HOME'] = p.get('config', 'HOME')
        self.raws[u'DEL'] = p.get('config', 'DEL')
        self.raws[u'END'] = p.get('config', 'END')
        self.raws[u'PAGEUP'] = p.get('config', 'PAGEUP')
        self.raws[u'PAGEDOWN'] = p.get('config', 'PAGEDOWN')
        self.raws[u'PRINT'] = p.get('config', 'PRINT')
        self.raws[u'SYSRQ'] = p.get('config', 'SYSRQ')
        self.raws[u'PAUSE'] = p.get('config', 'PAUSE')
        self.raws[u'BREAK'] = p.get('config', 'BREAK')
        self.raws[u'F1'] = p.get('config', 'F1')
        self.raws[u'F2'] = p.get('config', 'F2')
        self.raws[u'F3'] = p.get('config', 'F3')
        self.raws[u'F4'] = p.get('config', 'F4')
        self.raws[u'F5'] = p.get('config', 'F5')
        self.raws[u'F6'] = p.get('config', 'F6')
        self.raws[u'F7'] = p.get('config', 'F7')
        self.raws[u'F8'] = p.get('config', 'F8')
        self.raws[u'F9'] = p.get('config', 'F9')
        self.raws[u'F10'] = p.get('config', 'F10')
        self.raws[u'F11'] = p.get('config', 'F11')
        self.raws[u'F12'] = p.get('config', 'F12')
        self.raws[u'ARROWLEFT'] = p.get('config', 'ARROWLEFT')
        self.raws[u'ARROWRIGHT'] = p.get('config', 'ARROWRIGHT')
        self.raws[u'ARROWUP'] = p.get('config', 'ARROWUP')
        self.raws[u'ARROWDOWN'] = p.get('config', 'ARROWDOWN')
        # non-single character keys
        self.raws[u' '] = p.get('config', 'SPACE')
        self.raws[u'\a'] = p.get('config', r'\a')
        self.raws[u'\b'] = p.get('config', r'\b')
        self.raws[u'\f'] = p.get('config', r'\f')
        self.raws[u'\n'] = p.get('config', r'\n')
        self.raws[u'\r'] = p.get('config', r'\r')
        self.raws[u'\t'] = p.get('config', r'\t')
        self.raws[u'\v'] = p.get('config', r'\v')
        # special cases conflicting with the parser
        self.raws[u'#'] = p.get('config', 'HASH')
        self.raws[u'='] = p.get('config', 'EQUAL')
        self.raws[u':'] = p.get('config', 'COLON')
        self.raws[u';'] = p.get('config', 'SEMICOLON')
        # extended sign characters
        self.raws[u'°'] = p.get('config', 'DEGREE')
        self.raws[u'€'] = p.get('config', 'EURO')
        self.raws[u'§'] = p.get('config', 'PARAGRAPH')
        self.raws[u'²'] = p.get('config', 'SMALL2')
        self.raws[u'³'] = p.get('config', 'SMALL3')
        self.raws[u'´'] = p.get('config', 'AKZENT')
        # language specific
        self.raws[u'ß'] = p.get('config', 'DESZ')
        self.raws[u'Ä'] = p.get('config', 'DEUMLUA')
        self.raws[u'ä'] = p.get('config', 'DEUMLLA')
        self.raws[u'Ö'] = p.get('config', 'DEUMLUO')
        self.raws[u'ö'] = p.get('config', 'DEUMLLO')
        self.raws[u'Ü'] = p.get('config', 'DEUMLUU')
        self.raws[u'ü'] = p.get('config', 'DEUMLLU')
        for k, v in six.iteritems(self.raws):
            self.overrides[k] = self._raw_to_byte_array(v)


class DevControlServer(TcpServerBase, LoggerBase, RuntimeQuery, ThreadManager):
    def __init__(self, dummy_mode=False):
        TcpServerBase.__init__(self)
        RuntimeQuery.__init__(self)
        ThreadManager.__init__(self)
        LoggerBase.__init__(self, 'DevControlServer')
        self.socket_pool = list()
        self.props = dict()
        # load the correct driver adapter for each os
        if dummy_mode:
            self.logger.info("Dummy mode enabled: No data will be send to devices!")
            self.driver = DummyDriverAdapter()
        else:
            if platform.system() == 'Linux':
                self.driver = LinuxXServerAdapter()
            elif platform.system() == 'Windows':
                self.driver = WindowsAdapter()
            elif platform.system() == 'Darwin':
                self.driver = MacOSXAdapter()
            else:
                self.logger.warning("Unsupported System: No virtual devices are available!")
                self.driver = DummyDriverAdapter()

    def server_acceptor_handler(self, sock, address):
        """ Same functionality as the super-class-method plus thread-management.

        :type address: tuple of (str, int)
        :type sock: socket._socketobject
        :param sock:  the socket of the new connection
        :param address: the address, port tuple of the connection
        """
        self.logger.info("accepted connection from: %s", address)
        # print 'accepted connection from: ', address
        self.socket_pool.append(sock)
        self.create_thread(self.dev_control_server_processor_thread, (sock,))
        # check if any thread has ceased to exist
        self.cleanup_threads()

    def dev_control_server_processor_thread(self, sock):
        """ This is the bot side message listener thread.

        :type sock: socket._socketobject
        :param sock: the socket to work with
        """
        while self.active:
            msg = NetUtility.receive_prefixed_message(sock)
            cmd = json.loads(msg)
            try:
                if cmd['cmd'] == 'get_properties':
                    self.get_props(sock)
                elif cmd['cmd'] == 'set_property':
                    self.set_prop(cmd['property'], cmd['value'])
                elif cmd['cmd'] == 'kb_send_text':
                    self.driver.kb_write_text(cmd['text'])
                elif cmd['cmd'] == 'kb_send_special_key':
                    self.driver.kb_write_special_key(cmd['lctrl'], cmd['lalt'], cmd['lshift'], cmd['ralt'], cmd['lgui'],
                                                     cmd['rgui'], cmd['key'])
                elif cmd['cmd'] == 'kb_send_scan_codes':
                    self.driver.kb_write_scancode(cmd['scan_codes'])
                elif cmd['cmd'] == 'mouse_move_relative':
                    self.driver.mouse_move_relative(cmd['x'], cmd['y'])
                elif cmd['cmd'] == 'mouse_click':
                    self.driver.mouse_click(cmd['left'])
                elif cmd['cmd'] == 'mouse_double_click':
                    self.driver.mouse_double_click(cmd['left'])
                elif cmd['cmd'] == 'mouse_hold':
                    self.driver.mouse_hold(cmd['left'])
                elif cmd['cmd'] == 'mouse_release':
                    self.driver.mouse_release(cmd['left'])
                elif cmd['cmd'] == 'dbg_dump_mapper':
                    self.dbg_dump_mapper(sock)
                else:
                    pass
            except KeyError:
                pass
            except socket.error as e:
                self.logger.error("Socket Error: ", e)
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                break
            except RuntimeError as e:
                if e.message == 'unexpected connection close':
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except socket.error:
                        pass
                    finally:
                        sock.close()
                        self.logger.info("socket has been closed by demand")
                        break
                else:
                    raise RuntimeError(e.message)

    def dbg_dump_mapper(self, sock):
        p = six.moves.cPickle.dumps(self.driver.translator.mapper)  # apparently json cannot dump byte-arrays, need to pickle it
        # msg = json.dumps(p)
        sock.send(NetUtility.length_prefix_message(p))

    def get_props(self, sock):
        """ Send back all properties.

        :param sock: socket to send data to
        """
        msg = json.dumps(self.props)
        sock.send(NetUtility.length_prefix_message(msg))

    def set_prop(self, prop, value):
        """ Sets and evaluates a property

        :type prop: str
        :type value: str
        :param prop: the property to set
        :param value: the value to set
        """
        if prop == 'adapter':
            # if value == 'linux-console':
            #    self.driver = LinuxConsoleAdapter()
            #    self.props['support_keyboard'] = True
            #    self.props['kb_keymap'] = 'generic'
            #    self.props['support_mouse_relative'] = False
            #    self.props['support_mouse_absolute'] = False
            #    self.props['adapter'] = value
            if value == 'linux-xserver':
                self.driver = LinuxXServerAdapter()
                self.props['support_keyboard'] = True
                self.props['kb_keymap'] = 'de'
                self.props['support_mouse_relative'] = True
                self.props['support_mouse_absolute'] = False
                self.props['adapter'] = value
            elif value == 'linux-wayland':
                pass
            elif value == 'windows':
                pass
            elif value == 'macosx':
                pass
            elif value == 'dummy':
                self.driver = DummyDriverAdapter()
                self.props['support_keyboard'] = True
                self.props['kb_keymap'] = 'generic'
                self.props['support_mouse_relative'] = True
                self.props['support_mouse_absolute'] = False
                self.props['adapter'] = value
            else:
                pass
        else:
            pass

    def start(self, bind_ip='', bind_port=DEV_PORT):
        """ Starts the server.

        :type bind_port: int
        :type bind_ip: str
        :param bind_ip: the address we want the agent to bind to
        :param bind_port: the port we want the agent to bind to
        """
        self.active = True
        self.stopped = False
        self.server_start_listener(bind_port, bind_ip)
        self.logger.info("started dev server listener")

    def stop(self):
        """ Stops the server.


        """
        self.logger.info("shutting dev server down")
        self.active = False
        self.server_stop_listener()
        for s in self.socket_pool:
            try:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            except socket.error:
                pass
        self.join_all_threads()
        self.stopped = True
        self.logger.info("dev shutdown complete")


class DevControlClient(TcpClientBase):
    """ A class for sending input to a guest

    """

    def __init__(self):
        """

        """
        TcpClientBase.__init__(self)

    def connect(self, guest, port=DEV_PORT, timeout=None):
        """ Opens a connection to the DevControlServer.

        :type guest: fortrace.core.guest.Guest | str
        :type port: int
        :type timeout: float | None
        :param timeout: time to wait till connection is established
        :param port: target port
        :param guest: target guest or ip-address

        """
        if isinstance(guest, Guest):
            ip_address = str(guest.ip_local)
        else:
            ip_address = guest
        self.client_open_connection(ip_address, port, timeout)

    def close(self):
        """ Closes connection to the DevControlServer.

        """
        self.client_close_connection()

    def dbg_dump_mapper(self):
        cmd = dict()
        cmd['cmd'] = 'dbg_dump_mapper'
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)
        msg = NetUtility.receive_prefixed_message(self.client_socket)
        return six.moves.cPickle.loads(msg)

    def set_property(self, prop, value):
        """ Sets a property.

        :type prop: str
        :type value: str
        :param prop:
        :param value:
        """
        cmd = dict()
        cmd['cmd'] = 'set_property'
        cmd['property'] = prop
        cmd['value'] = value
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    def get_properties(self):
        """ Get device properties from the DevControlServer.

            :rtype dict
            :return a dict containing properties
        """
        cmd = dict()
        cmd['cmd'] = 'get_properties'
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)
        msg = NetUtility.receive_prefixed_message(self.client_socket)
        return json.loads(msg)

    def kb_send_text(self, text):
        """ Sends an array of ascii chars to the server.

        :type text: str
        :param text: the input to be send
        """
        cmd = dict()
        cmd['cmd'] = 'kb_send_text'
        cmd['text'] = text
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    def kb_send_special_key(self, key, lctrl=False, lalt=False, lshift=False, ralt=False, lgui=False, rgui=False):
        """ Send a single alphanumeric key with modifiers.

        :type key: str
        :type rgui: bool
        :type lgui: bool
        :type ralt: bool
        :type lshift: bool
        :type lalt: bool
        :type lctrl: bool
        :param lctrl: the lctrl key
        :param lalt: the left lalt key or just lalt
        :param lshift: the lshift key
        :param ralt: the right lalt key
        :param lgui: the lgui key or the commonly know windows key
        :param lgui: the rgui key or the commonly know menu key (right click menu)
        :param key: a single character or a value from SpecialAndFunctionKeys list
        """
        assert len(key) > 0
        tmp_key = key
        if len(key) > 1:
            if not key.upper() in SpecialAndFunctionKeys:
                raise RuntimeError(
                    "Unsupported key value, use either a single character or a value from the following list: " + str(
                        SpecialAndFunctionKeys))
            else:
                tmp_key = key.upper()
        # do some filtering
        if tmp_key == "SYSRQ":  # is actually lalt+print
            tmp_key = "PRINT"
            lalt = True
        elif tmp_key == "BREAK":  # is actually lalt+pause
            tmp_key = "PAUSE"
            lalt = True
        cmd = dict()
        cmd['cmd'] = "kb_send_special_key"
        cmd['lctrl'] = lctrl
        cmd['lalt'] = lalt
        cmd['lshift'] = lshift
        cmd['ralt'] = ralt
        cmd['lgui'] = lgui
        cmd['rgui'] = rgui
        cmd['key'] = tmp_key
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    def kb_send_scan_codes(self, scan_codes):
        """ Sends raw scan codes or data frames for an user-space application.
            Mainly used for debugging.

        :type scan_codes: bytearray
        :param scan_codes: an array of raw scan code
        """
        cmd = dict()
        cmd['cmd'] = 'kb_send_scan_codes'
        cmd['scan_codes'] = scan_codes
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    def mouse_move_relative(self, x, y):
        """ Moves the mouse cursor.
            Note: These are raw movement vectors.
            Windows will follow computer graphic coordinate vectors (y-axis is aligned downward).
            Linux will follow cartesian coordinate vectors (y-axis is aligned upward).

        :type x: int
        :type y: int
        :param x: x-direction (8-bit range), positive means right movement, negative left movement
        :param y: y-direction (8-bit range), linux: positive means up, negative down - windows: inverse of linux
        """
        cmd = dict()
        cmd['cmd'] = 'mouse_move_relative'
        cmd['x'] = DevControlClient._signed_byte_to_unsigned_byte(x)
        cmd['y'] = DevControlClient._signed_byte_to_unsigned_byte(y)
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    def mouse_click(self, left=True):
        """ Clicks a mouse button.

        :type left: bool
        :param left: is this a left click
        """
        cmd = dict()
        cmd['cmd'] = 'mouse_click'
        cmd['left'] = left
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    def mouse_double_click(self, left=True):
        """ Clicks a mouse button.

        :type left: bool
        :param left: is this a left click
        """
        cmd = dict()
        cmd['cmd'] = 'mouse_double_click'
        cmd['left'] = left
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    def mouse_hold(self, left=True):
        """ Hold a mouse button.

        :type left: bool
        :param left: is this a left click
        """
        cmd = dict()
        cmd['cmd'] = 'mouse_hold'
        cmd['left'] = left
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    def mouse_release(self, left=True):
        """ Release a mouse button

        :type left: bool
        :param left: is this a left click
        """
        cmd = dict()
        cmd['cmd'] = 'mouse_release'
        cmd['left'] = left
        msg = json.dumps(cmd)
        msg = NetUtility.length_prefix_message(msg)
        self.client_socket.send(msg)

    @staticmethod
    def _signed_byte_to_unsigned_byte(value):
        """ Converts a signed byte to unsigned byte represented as integers.

        :type value: int
        :param value: an integer in range of -128 to 127
        :return: int
        """
        b = struct.pack("b", value)
        return struct.unpack("B", b)[0]
