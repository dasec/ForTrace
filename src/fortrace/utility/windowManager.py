from __future__ import absolute_import
from ldtp import launchapp, waittillguiexist, activatewindow, settextvalue, check, click, closewindow, generatekeyevent


class LinuxWindowManager(object):
    def start(self, app, blockingTitle=None, args=None):
        """Starts :app and optionally blocks until window opens
            :blockingTitle title of window to wait for
        """
        if args is None:
            args = []
        launchapp(app, args)

        if blockingTitle:
            waittillguiexist(blockingTitle)

    def focus(self, window):
        """Change focus to window with title :window
            :returns True if successfully, otherwise False
        """
        focusState = (1 == activatewindow(window))
        return focusState

    def text(self, window, textId, text):
        """Inserts :text into text-box :textId of :window"""
        settextvalue(window, textId, text)

    def check(self, window, checkboxId):
        """Toggles radio-checkbox :checkboxId of :window"""
        check(window, checkboxId)

    def click(self, window, componentId):
        """Left-click on component :componentId of :window"""
        click(window, componentId)

    def close(self, window):
        """Close window with given title :window
            will close all windows if empty
        """
        closewindow(window)

    def waitforwindow(self, window, timeout=None):
        """Waits until window with title :window appears. With :timeout it is possible to
            limit the time in seconds to wait before returning even if the window does not appear
            :returns true on success, false otherwise
        """
        return 1 == waittillguiexist(window, guiTimeOut=timeout)

    def sendkeys(self, keys):
        """Sends keys from :keys String. See
        `LDTP generatekeyevent documentation <http://ldtp.freedesktop.org/user-doc/d7/d6e/a00190.html>`_
        for a list of supported key-events.
        """
        generatekeyevent(keys)
