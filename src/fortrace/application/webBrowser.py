# Copyright (C) 2013-2014 Reinhard Stampp
# This file is part of fortrace - http://fortrace.fbi.h-da.de
# See the file 'docs/LICENSE' for copying permission.

from __future__ import absolute_import
from __future__ import print_function
try:
    import logging
    import sys
    import platform
    import threading
    import subprocess
    import inspect  # for listing all method of a class
    import os

    # base class VMM side
    from fortrace.application.application import ApplicationVmmSide
    from fortrace.application.application import ApplicationVmmSideCommands

    # base class guest side
    from fortrace.application.application import ApplicationGuestSide
    from fortrace.application.application import ApplicationGuestSideCommands
    from fortrace.utility.line import lineno

    if platform.system() == "Windows":
        # Web browser stuff like selenium to control the browser on the guest
        # from fortrace.core.agent import Agent
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys
        from fortrace.utility.seleniumkeys import translate_winKeys_to_seleniumKeys

except ImportError as ie:
    print(("Import error! in webBrowser.py " + str(ie)))
    exit(1)


###############################################################################
# Host side implementation
###############################################################################
class WebBrowserVmmSide(ApplicationVmmSide):
    """
    This class is a remote control on the host-side to control a real browser
    running on a guest. Supported browsers on the guest are Mozilla Firefox, Google
    Chrome. For more details to the correspond guest-side module look into
    webBrowser_guest_side.

    """

    def __init__(self, guest_obj, args):
        """Set default attribute values only.
        @param guest_obj: The guest on which this browser is running. (will be inserted from guest::application())
        @param args: containing
                web_browser : Type of the webBrowser (currently firefox is
                    tested).
                 logger: Logger name for logging.

        """
        try:
            super(WebBrowserVmmSide, self).__init__(guest_obj, args)
            self.logger.info("function: WebBrowserVmmSide::__init__")
            # surf the url through the socket.
            self.webBrowser = args['webBrowser']
            # the current link which was surfed
            self.url = None
            self.window_id = None

        except Exception as e:
            raise Exception(
                lineno() + " Error: webBrowserHostSide::__init__ " + self.guest_obj.guestname + " " + str(e))

    def open(self, url):
        """Sends a command to open a webBrowser on the associated guest.

        @param url: Website to open.

        """
        # store the current window_id from the guest object as this browser window_id,
        # start the browser and
        # increment the window id from the guest object
        try:
            self.logger.info("function: WebBrowserVmmSide::open")
            self.url = url
            self.window_id = self.guest_obj.current_window_id
            self.guest_obj.send(
                "application " + "webBrowser " + str(self.window_id) + " open " + self.webBrowser + " " + self.url)

            self.guest_obj.current_window_id += 1

        except Exception as e:
            raise Exception("error WebBrowserVmmSide::open: " + str(e))

    def close(self):
        """Sends a command to close a webBrowser on the associated guest.

        """
        try:
            self.logger.info("function: WebBrowserVmmSide::close")
            self.guest_obj.send("application " + "webBrowser " + str(self.window_id) + " close ")
        except Exception as e:
            raise Exception("error WebBrowserVmmSide:close()" + str(e))

    def browse_to(self, url):
        """Sends a url to the associated webBrowser running on the guest.
        @param url: URL to load.

        """
        try:
            self.logger.info("function: WebBrowserVmmSide::browse_to")
            self.guest_obj.send("application " + "webBrowser " + str(self.window_id) + " browse_to " + url)
            self.is_busy = True
        except Exception as e:
            raise Exception("error WebBrowserVmmSide::browse_to: " + str(e))

    def browse_to_link_number(self, link_number):
        """Call the <linkNumber> link on the current website in the browser.
        @param link_number: number of the link on this website to call.

        """
        try:
            self.logger.info("function: WebBrowserVmmSide::browse_to_link_number")
            self.guest_obj.send(
                "application " + "webBrowser " + str(self.window_id) + " browse_to_link_number " + str(link_number))
            self.is_busy = True
        except Exception as e:
            raise Exception("error WebBrowserVmmSide::browse_to_link_number: " + str(e))

    def send_keys_to_browser_element(self, element, keys):
        """Send keys to a specific element on the currently parsed website.
        @param element: element to search for.
        @param keys: string for the element

        """
        try:
            self.logger.info("function: WebBrowserVmmSide::send_keys_to_browser_element")
            self.guest_obj.send("application " + "webBrowser " + str(
                self.window_id) + " send_keys_to_browser_element" + " " + element + " " + keys)

        except Exception as e:
            raise Exception("error WebBrowserVmmSide::send_keys_to_browser_element: " + str(e))

    def facebook_login(self, username, password):
        """Sends a command to call facebook.com and login.
        @param username: facebook username.
        @param password: facebook password.

        """
        try:
            self.logger.info("function: WebBrowserVmmSide::facebook_login")
            self.browse_to("www.facebook.com")
            self.send_keys_to_browser_element("email", username)
            self.send_keys_to_browser_element("pass", password)
            self.send_keys_to_browser_element("pass", "{ENTER}")
        except Exception as e:
            raise Exception("error WebBrowserVmmSide::facebook_login: " + str(e))


###############################################################################
# Commands to parse on host side
###############################################################################
class WebBrowserVmmSideCommands(ApplicationVmmSideCommands):
    """
    Class with all commands for webBrowser which will be received from the agent on the guest.

    Static only.

    """

    @staticmethod
    def commands(guest_obj, cmd):
        # cmd[0] = win_id; cmd[1] = state
        module_name = "webBrowser"
        guest_obj.logger.debug("WebBrowserVmmSideCommands::commands: " + cmd)
        cmd = cmd.split(" ")
        try:
            if "opened" in cmd[1]:
                guest_obj.logger.debug("in opened")
                for obj in guest_obj.applicationWindow[module_name]:
                    if cmd[0] == str(obj.window_id):
                        guest_obj.logger.debug("window_id: " + str(obj.window_id) + " found!")
                        guest_obj.logger.info(module_name + " with id: " + str(obj.window_id) + " is_opened = true")
                        obj.is_opened = True
                        guest_obj.logger.debug("browser_obj.is_opened is True now!")

            if "busy" in cmd[1]:
                guest_obj.logger.debug("in busy")
                for obj in guest_obj.applicationWindow[module_name]:
                    if cmd[0] == str(obj.window_id):
                        guest_obj.logger.info(module_name + " with id: " + str(obj.window_id) + " is_busy = true")
                        obj.is_busy = True

            if "ready" in cmd[1]:
                guest_obj.logger.debug("in ready")
                for obj in guest_obj.applicationWindow[module_name]:
                    if cmd[0] == str(obj.window_id):
                        guest_obj.logger.info(module_name + " with id: " + str(obj.window_id) + " is_busy = false")
                        obj.is_busy = False

            if "error" in cmd[1]:
                guest_obj.logger.debug("in error")
                for obj in guest_obj.applicationWindow[module_name]:
                    if cmd[0] == str(obj.window_id):
                        guest_obj.logger.info(module_name + " with id: " + str(obj.window_id) + " has_error = True")
                        obj.has_error = True

        except Exception as e:
            raise Exception(module_name + "_host_side_commands::commands " + str(e))


###############################################################################
# Guest side implementation
###############################################################################
class WebBrowserGuestSide(ApplicationGuestSide):
    """webBrowser implementation of the guest side.

    Usually Windows, Linux guest's
    class attributes
    browserType - Which browser have to be used for surfing (firefox, chrome...)
    window_id - The ID for the opened object
    url - which have to be opened / is opened

    """

    def __init__(self, agent_obj, logger):
        super(WebBrowserGuestSide, self).__init__(agent_obj, logger)
        try:
            self.browserType = None
            self.url = None
            self.last_driven_url = None
            self.last_browser_type = None
            self.seleniumDriver = None
            self.module_name = "webBrowser"
            self.timeout = None
            self.window_is_crushed = None
            self.window_id = None
            self.agent_object = agent_obj

        except Exception as e:
            raise Exception("Error in " + self.__class__.__name__ +
                            ": " + str(e))

    def open(self, args):
        """
        Open a browser and save the webBrowser object with an id in a dictionary.
        Set page load timeout to 30 seconds.

        return:
            Send to the host in the known to be good state:
                'application webBrowser window_id open'.
                'application webBrowser window_id ready'.
            in the error state:
                'application webBrowser window_id error'.
            additionally the 'window_is_crushed' attribute is set; so the next
            call will open a new window.

        """
        try:
            arguments = args.split(" ")
            web_browser = arguments[0]
            url = arguments[1]

            if len(arguments) > 2:
                self.timeout = arguments[2]
            else:
                self.timeout = 30

            self.logger.info(self.module_name + "GuestSide::open")
            self.last_driven_url = url
            self.logger.debug("URL to call: " + url)
            if web_browser == "firefox":
                self.logger.debug("wait for start selenium firefox webdriver...")
                self.seleniumDriver = webdriver.firefox.webdriver.WebDriver(
                    firefox_profile=None, firefox_binary=None,
                    timeout=self.timeout, capabilities=None, proxy=None)
                self.logger.debug("started!")
            elif web_browser == "chrome":
                self.logger.debug("start selenium chrome webdriver...")
                self.seleniumDriver = webdriver.Chrome()
                self.logger.debug("started!")
            else:
                self.logger.error("Browser type " + web_browser +
                                  " not implemented")
                return

            self.seleniumDriver.set_page_load_timeout(30)
            self.logger.info("open url: " + url)
            if "http" not in url:
                url = "http://" + url
            self.seleniumDriver.get(url)

            # send some information about the browser state
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " opened")

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info("WebBrowserGuestSide::open: Close all open browsers and clear the webBrowser list")
            subprocess.call(["taskkill", "/IM", "firefox.exe", "/F"])
            # for browserObject in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(browserObject)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ + "::open" + ": selenium is crushed: " + str(e))

    def close(self, args):
        """Close one given browser by window_id

        @param args: Not used, only inserted for the generic function

        """
        self.logger.info(self.__class__.__name__ +
                         "::close ")
        self.seleniumDriver.quit()

    def browse_to(self, url):
        """Will browse to the url with the browser window which have the given window_id

        Send to the host in the known to be good state:
            'browserInfo busy window_id'   before load the website.
            'browserInfo ready window_id'  if load is finished.
        in the error state:
            'browserInfo error window_id'  if selenium will throw an exception.
        additionally the 'window_is_crushed' attribute is set; so the next
        browse call will open a new window.

        """
        try:
            self.last_driven_url = url
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            self.seleniumDriver.get(url)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info("WebBrowserGuestSide::browse_to: Close all open browsers and clear the webBrowser list")
            subprocess.call(["taskkill", "/IM", "firefox.exe", "/F"])
            # for browserObject in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(browserObject)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ + "::open" + ": selenium is crushed: " + str(e))

    def browse_to_link_number(self, link_number):
        """Parse the website to find <a> elements which represent a link.

        Sends a busy and ready message to the VMM.
        It surf the linkNumbers link by clicking it.

        """
        try:
            self.logger.info("function: browse_to_link_number")
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            link_list = self.seleniumDriver.find_elements_by_tag_name('a')
            while len(link_list) > int(link_number):
                if link_list[int(link_number)].is_displayed():
                    link_list[int(link_number)].click()
                    break
                else:
                    self.logger.warning("not visible" + str(link_number))
                    link_number = int(link_number) + 1
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info(
                "WebBrowserGuestSide::browse_to_link_nuber: Close all open browsers and clear the " + "webBrowser list")
            subprocess.call(["taskkill", "/IM", "firefox.exe", "/F"])
            # for browserObject in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(browserObject)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ + "::open" + ": selenium is crushed: " + str(e))

    def browse_to_link_name(self, link_name):
        """Parse the website to find <a> elements which represent a link.
        Sends a busy and ready message to the host
        Then it surf the linkNumbers link by clicking it.

        """
        try:

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            continue_link = self.seleniumDriver.find_element_by_link_text(
                link_name)
            if continue_link.is_displayed():
                continue_link.click()

            else:
                self.logger.warning("not visible" + str(link_name))
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
            self.window_is_crushed = False
        except Exception as e:
            self.logger.info(
                "WebBrowserGuestSide::browse_to_link_name: Close all open browsers and clear the " + "webBrowser list")
            subprocess.call(["taskkill", "/IM", "firefox.exe", "/F"])
            # for browserObject in self.agent_object.applicationWindow[self.module_name]:
            #    self.agent_obj.applicationWindow[self.module_name].remove(browserObject)
            # set a crushed flag.
            self.window_is_crushed = True
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")
            self.logger.error("Error in " + self.__class__.__name__ + "::open" + ": selenium is crushed: " + str(e))

    def send_keys_to_browser_element(self, args):
        """Send Keys to an browser element, searched by selenium.

        """
        try:
            arguments = args.split(" ")
            element = arguments[1]
            keys = arguments[2]

            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " busy")
            elem = self.seleniumDriver.find_element_by_name(element)
            key_string = translate_winKeys_to_seleniumKeys(keys)
            elem.send_keys(key_string)
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " ready")
        except Exception as e:
            self.logger.error(self.module_name + " error " + str(self.window_id) + str(e))
            self.agent_object.send("application " + self.module_name + " " + str(self.window_id) + " error")


###############################################################################
# Commands to parse on guest side
###############################################################################
class WebBrowserGuestSideCommands(ApplicationGuestSideCommands):
    """
    Class with all commands for one application.

    call the ask method for an object. The call will be done by a thread, so if the timeout is
    reached, the open application will be closed and opened again.
    Static only.

    """

    @staticmethod
    def commands(agent_obj, obj, cmd):  # commands(obj, cmd) obj from list objlist[window_id] win id in cmd[1]?
        try:
            agent_obj.logger.info("static function WebBrowserGuestSideCommands::commands")
            agent_obj.logger.debug("command to parse: " + cmd)
            com = cmd.split(" ")
            if len(com) > 3:
                args = " ".join(com[3:])

            module = com[0]  # inspect.stack()[-1][1].split(".")[0]
            window_id = com[1]
            method_string = com[2]

            method_found = False
            methods = inspect.getmembers(obj, predicate=inspect.ismethod)

            for method in methods:
                # method[0] will now contain the name of the method
                # method[1] will contain the value

                if method[0] == method_string:
                    # start methods as threads
                    method_found = True
                    agent_obj.logger.debug("method to call: " + method[0] + "(" + args + ")")
                    agent_obj.logger.debug("args")
                    tmp_thread = threading.Thread(target=method[1], args=(args,))
                    agent_obj.logger.debug("thread is defined")
                    tmp_thread.start()
                    agent_obj.logger.debug("thread started")
                    tmp_thread.join(50)  # Wait until the thread is completed
                    if tmp_thread.is_alive():
                        agent_obj.logger.error("thread is alive... time outed")
                        # close open tasks (browser...)
                        # Todo close open function and windows
                        agent_obj.logger.info(
                            "WebBrowserGuestSideCommands::commands: Close all open browsers and " + "clear the webBrowser list")
                        if platform.system() == "Windows":
                            subprocess.call(["taskkill", "/IM", "firefox.exe", "/F"])
                        elif platform.system() == "Linux":
                            os.system("pkill firefox")
                        else:
                            raise NotImplemented("Not implemented for system: " + platform.system())
                        # for browserObject in agent_obj.applicationWindow[module]:
                        #    agent_obj.applicationWindow[module].remove(browserObject)
                        # set a crushed flag.
                        obj.is_opened = False
                        obj.is_busy = False
                        obj.has_error = True

                        agent_obj.logger.info("application " + module + " " + str(window_id) + " error")
                        agent_obj.send("application " + module + " " + str(window_id) + " error")

            if not method_found:
                raise Exception("Method " + method_string + " is not defined!")
        except Exception as e:
            raise Exception("Error in WebBrowserGuestSideCommands::commands " + str(e))
