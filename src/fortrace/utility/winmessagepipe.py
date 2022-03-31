from __future__ import absolute_import
import platform
if platform.system() == "Windows":
    import win32pipe
    import win32file
    import win32api
    import ntsecuritycon
    import pywintypes
    import time
else:
    raise RuntimeError("This module is ony supported on Windows!")

DEFAULT_PIPE_PREFIX = "\\\\.\\pipe\\LOCAL\\"


class WinMessagePipe(object):
    """ A wrapper for message mode IPC using named pipes on Windows.

    """
    def __init__(self):
        self._pipe = None
        self._pipename = ""
        self._mode = "r"

    def open(self, pipename, mode='r'):
        """ Opens a named pipe in the LOCAL pipe namespace.
            Clients will block till pipe is connected.

        :rtype pipename: str
        :rtype mode: str
        :param pipename: name for the pipe, namespace is not required and is prefixed by function
        :param mode: either r for clients or w for servers
        """
        self._pipename = DEFAULT_PIPE_PREFIX + pipename
        self._mode = mode
        if mode == 'w':
            self._pipe = win32pipe.CreateNamedPipe(self._pipename, win32pipe.PIPE_ACCESS_OUTBOUND,
                                                   win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                                                   win32pipe.PIPE_UNLIMITED_INSTANCES, 512, 512,
                                                   win32pipe.NMPWAIT_WAIT_FOREVER, None)
            if self._pipe == win32file.INVALID_HANDLE_VALUE:
                self._pipe = None
                raise OSError("Invalid pipe handle value, error: " + str(win32api.GetLastError()))
        elif mode == 'r':
            while True:
                try:
                    self._pipe = win32file.CreateFile(self._pipename,
                                                      win32file.GENERIC_READ | ntsecuritycon.FILE_WRITE_ATTRIBUTES,
                                                      win32file.FILE_SHARE_READ, None, win32file.OPEN_EXISTING,
                                                      win32file.FILE_ATTRIBUTE_NORMAL, None)
                    if self._pipe == win32file.INVALID_HANDLE_VALUE:
                        self._pipe = None
                        raise OSError("Invalid pipe handle value, error: " + str(win32api.GetLastError()))
                    break
                except OSError:
                    pass
                except pywintypes.error:
                    time.sleep(0.1)
        else:
            raise RuntimeError("unsupported open mode use either r or w")

    def close(self):
        """ Close Pipe and associated handle.

        """
        if self._pipe is not None:
            try:
                win32pipe.DisconnectNamedPipe(self._pipe)
            except pywintypes.error:  # clients may trow error if pipe is already disconnected
                pass
            win32api.CloseHandle(self._pipe)
            self._pipe = None

    def read(self):
        """ Read a message from pipe.

        :rtype: str
        :return: a pipe message
        """
        if self._pipe is not None:
            while True:
                try:
                    hr, data = win32file.ReadFile(self._pipe, 512, None)
                    break
                except pywintypes.error as d:
                    if d[0] == 233:  # pipe broken
                        raise OSError("Broken pipe!")
                    elif d[0] == 232:  # pipe closing
                        raise OSError("Pipe is shutting down!")
            if hr == 0:
                return data
        else:
            raise RuntimeError("Pipe has no handle!")

    def write(self, data):
        """ Write a message to pipe.

        :type data: str
        :param data: a string containing data
        :rtype: int
        :return: length of the send data
        """
        if self._pipe is not None:
            try:
                err, length = win32file.WriteFile(self._pipe, data, None)
                if err == 0:
                    return length
            except pywintypes.error as d:
                if d[0] == 536:  # no listener
                    raise OSError("Pipe is not connected! [536]")
                elif d[0] == 232:  # pipe closing
                    raise OSError("Pipe is shutting down! [232]")
                else:
                    raise OSError("Other error writing to pipe! [" + str(d[0]) + "]")
        else:
            raise RuntimeError("Pipe has no handle!")

    def server_wait_for_client(self):
        """ Blocks till a client connects to the server.

        :rtype: bool
        :return: success of this function
        """
        if self._mode == 'w':
            if self._pipe is not None:
                try:
                    r = win32pipe.ConnectNamedPipe(self._pipe, None)
                    if r == 0:
                        return True
                    else:
                        return False
                except pywintypes.error as e:
                    return False
            else:
                raise RuntimeError("Pipe has no handle!")
        else:
            raise RuntimeError("You may only call this method on a server write instance!")