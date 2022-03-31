""" Module to interact with firefox via marionette web-api.
    Note: window may refer to windows, chrome-windows or tabs
          It is not guaranteed that indexes have an incremental numbering or keep the same id over the session

"""
from __future__ import absolute_import
import sys
from marionette_driver.errors import InvalidSessionIdException
from marionette_driver.marionette import Marionette
from marionette_driver import By
from marionette_driver.errors import NoSuchElementException
from marionette_driver.errors import TimeoutException
from marionette_driver.errors import NoSuchWindowException
from marionette_driver.errors import ElementNotInteractableException
from marionette_driver.errors import ElementNotAccessibleException
from marionette_driver.errors import ElementNotSelectableException
from marionette_driver.errors import ElementNotVisibleException
from marionette_driver.errors import InsecureCertificateException
from marionette_driver.errors import UnknownException
import subprocess
import time
import logging
import socket
import six

DEFAULT_FF_PATH_LINUX = '/usr/bin/firefox'
DEFAULT_FF_PATH_WIN32 = 'C:/Program Files/Mozilla Firefox/firefox.exe'
DEFAULT_FF_PATH_WIN64 = 'C:/Program Files (x86)/Mozilla Firefox/firefox.exe'
DEFAULT_FF64_PATH_WIN = 'C:/Program Files/Mozilla Firefox/firefox.exe'


class MarionetteHelper:
    """ Helper for starting firefox and for remote browsing

    """

    def __init__(self, firefox_path, logger=None):
        self.logger = logger  # type: logging.Logger
        self.client = None  # type: Marionette
        self.ffpopen = None  # type: subprocess.Popen
        self.ffpath = firefox_path  # type: str
        if logger is None:
            self.logger = logging.getLogger("MarionetteHelper")
        self.logger.debug("Marionette helper init done")

    def _open_session(self, host='localhost', port=2828):
        """ Opens the session for marionette"""
        caps = {u'acceptInsecureCerts': True, }
        self.client = Marionette(host, port=port)
        self.client.start_session(capabilities=caps)

    def run_firefox(self):
        """ Start the firefox process"""
        self.logger.debug("Starting firefox process")
        self.ffpopen = subprocess.Popen([self.ffpath, "-marionette"])
        self.logger.debug("Opening marionette session")
        self._open_session()

    def quit_firefox(self):
        """ Close the firefox process and close marionette session"""
        #self.logger.debug("Closing firefox")
        #self.client._send_message("Marionette:Quit")
        self.client._request_in_app_shutdown("eForceQuit")
        self.client.delete_session(False)
        self.client.cleanup()
        self.client = None # reset client state
        #try:
        #    self.client.close()  # try to close the window anyway
        #except InvalidSessionIdException:
        #    pass
        #except socket.error:
        #    pass
        #finally:
        #    try:
        #        self.logger.debug("Closing marionette session")
        #        self.client.delete_session(False)  # close client session
        #    except InvalidSessionIdException:
        #        pass
        #    except socket.error:
        #        pass
        #    self.client = None  # reset client state
        #self.logger.debug("Waiting for firefox to close")
        #for _ in range(3):  # give the process 3 seconds to terminate
        #    time.sleep(1)
        #    self.ffpopen.poll()
        #    if self.ffpopen.returncode is not None:
        #        break
        #self.ffpopen.poll()
        #if self.ffpopen.returncode is None:
        #    self.logger.warning("Firefox not closed in time, killing it!")
        #    self.ffpopen.kill()  # process was not quit in time, kill it
        #self.ffpopen = None  # reset popen state
        #self.logger.debug("Firefox is closed")

    def ___get_client(self):
        """ Returns the internal marionette client object"""
        return self.client

    def navigate_to_url(self, url):
        """ Open an url in format of http[s]://example.com"""
        try:
            if "http" not in url:
                url = "http://" + url
            self.client.navigate(url)
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def back(self):
        """ Go a page backward"""
        try:
            self.client.go_back()
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def forward(self):
        """ Go a page forward"""
        try:
            self.client.go_forward()
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def follow_link(self, index=0):
        """ Click on a link"""
        try:
            links = self.client.find_elements(By.TAG_NAME, "a")
            links[index].click()
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except IndexError:
            self.logger.warning("Error: Out of bound")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def click_element_by_class_name(self, html_class_name):
        """ Click on first element via class name"""
        try:
            e = self.client.find_element(By.CLASS_NAME, html_class_name)
            e.click()
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def click_element_by_css_selector(self, css_selector):
        """ Click on first element via css selector"""
        try:
            e = self.client.find_element(By.CSS_SELECTOR, css_selector)
            e.click()
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def click_element_by_id(self, html_id):
        """ Click on first element via element id"""
        try:
            e = self.client.find_element(By.ID, html_id)
            e.click()
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def click_element_by_name(self, html_name):
        """ Click on first element via element name"""
        try:
            e = self.client.find_element(By.NAME, html_name)
            e.click()
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def click_element_by_tag_name(self, html_tag_name):
        """ Click on first element via tag name"""
        try:
            e = self.client.find_element(By.TAG_NAME, html_tag_name)
            e.click()
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def click_element_by_xpath(self, xpath):
        """ Click on first element via xpath"""
        try:
            e = self.client.find_element(By.XPATH, xpath)
            e.click()
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def click_element_by_link_text(self, html_link_text):
        """ Click on first element via link text"""
        try:
            e = self.client.find_element(By.LINK_TEXT, html_link_text)
            e.click()
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        except InsecureCertificateException:
            self.logger.warning("Warning: Insecure Certificate")
            return True
        except UnknownException as e:
            if "Reached error page" in str(e):
                self.logger.warning("Reached error page, ignoring...")
            else: # reraise, something very unexpected happened here
                t, v, tb = sys.exc_info()
                six.reraise(t, v, tb)
            return False
        return True

    def send_keys_to_element_by_name(self, name, text):
        """ Sends text to an element via name"""
        try:
            e = self.client.find_element(By.NAME, name)
            e.send_keys(text)
        except ElementNotVisibleException:
            self.logger.warning("Error: Element not visible")
            return False
        except ElementNotSelectableException:
            self.logger.warning("Error: Element not selectable")
            return False
        except ElementNotAccessibleException:
            self.logger.warning("Error: Element not accessible")
            return False
        except ElementNotInteractableException:
            self.logger.warning("Error: Element not interactable")
            return False
        except NoSuchElementException:
            self.logger.warning("Error: Element does not exist")
            return False
        except TimeoutException:
            self.logger.warning("Error: Timeout")
            return False
        return True

    def select_window(self, index):
        """ Switch window via index"""
        try:
            self.client.switch_to_window(self.client.window_handles[index])
        except NoSuchWindowException:
            self.logger.warning("Error: Window does not exist")
            return False
        return True

    def close_window(self):
        """ Close the current window"""
        self.client.close()  # this won't close the last window, call quit_firefox instead

    def get_current_window_index(self):
        """ Get current windows index"""
        return self.client.window_handles.index(self.client.current_window_handle)

    def new_tab(self):
        """ Open a new empty tab"""
        with self.client.using_context("chrome"):
            self.client.find_element(By.ID, "menu_newNavigatorTab").click()

    def new_window(self):
        """ Open a new empty window"""
        with self.client.using_context("chrome"):
            self.client.execute_script("window.open();")

    def close_tab(self):
        """ Close the current tab"""
        self.close_window()  # basically the same as close windows
