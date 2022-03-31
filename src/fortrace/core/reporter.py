from __future__ import absolute_import
from __future__ import print_function
try:
    from logging import DEBUG
    from fortrace.utility.logger_helper import create_logger
    import xml.etree.ElementTree as ET
    import platform
    import os
    import datetime
except Exception as e:
    raise RuntimeError("Error while loading modules: " + str(e))


class Reporter(object):
    """
    This class is responsible for the creation of a report for a case
    added by Thomas Schaefer in 2019
    """
    root = ""
    doc = ""
    mails = []
    downloads = []
    browsings = []
    container = []
    usermanagement = []
    filemanagement = []
    antiforensics = []
    chronological = []
    registry = []
    imagename = ""
    author = ""
    hash = ""
    date = ""
    baseimage = ""
    basehash = ""
    operatingSystem = ""

    def __init__(self):
        self.logger = create_logger("reporter", DEBUG)
        self.logger.info("Reporter has been loaded and can be used")
        self.root = ET.Element("root")
        self.date = datetime.datetime.today().strftime('%m-%d-%Y %H:%M')

    def add(self, tag, text):
        """
        Adding the given text to the tag-array in order to later add them to the ElementTree.
        :param tag: XML tag name
        :param text: value to add to the XML file
        :return:
        """
        if(tag == "mail"):
            self.mails.append(text)
            self.chronological.append(text)
        elif(tag == "download"):
            self.downloads.append(text)
            self.chronological.append(text)
        elif(tag == "browsings"):
            self.browsings.append(text)
            self.chronological.append(text)
        elif(tag == "veracrypt"):
            self.container.append(text)
            self.chronological.append(text)
        elif(tag == "usermanagement"):
            self.usermanagement.append(text)
            self.chronological.append(text)
        elif(tag == "registry"):
            self.registry.append(text)
            self.chronological.append(text)
        elif(tag == "anti-forensics"):
            self.antiforensics.append(text)
            self.chronological.append(text)
        elif (tag == "filemanagement"):
            self.filemanagement.append(text)
            self.chronological.append(text)
        elif (tag == "chronological"):
            self.chronological.append(text)
        elif(tag == "imagename"):
            self.imagename = text
        elif (tag == "author"):
            self.author = text
        elif (tag == "hash"):
            self.hash = text
        elif (tag == "baseimage"):
            self.baseimage = text
        elif (tag == "basehash"):
            self.basehash = text
        elif (tag == "operatingSystem"):
            self.operatingSystem = text
        else:
            print("unknown tag.")

    def generateTags(self):
        """
        Adding the needed tags and values to the ElementTree (ET) to write them to a file.
        :return:
        """
        self.doc = ET.SubElement(self.root, "general")
        ET.SubElement(self.doc, "imagename").text = self.imagename
        ET.SubElement(self.doc, "author").text = self.author
        if self.hash:
            ET.SubElement(self.doc, "hash").text = self.hash
        if self.date:
            ET.SubElement(self.doc, "date").text = self.date
        if self.baseimage:
            ET.SubElement(self.doc, "baseimage").text = self.baseimage
        if self.basehash:
            ET.SubElement(self.doc, "basehash").text = self.basehash
        if self.operatingSystem:
            ET.SubElement(self.doc, "operatingSystem").text = self.basehash

        if self.mails:
            self.doc = ET.SubElement(self.root, "mails")
            for mail in self.mails:
                ET.SubElement(self.doc, "mail").text = mail

        if self.downloads:
            self.doc = ET.SubElement(self.root, "downloads")
            for download in self.downloads:
                ET.SubElement(self.doc, "download").text = download

        if self.browsings:
            self.doc = ET.SubElement(self.root, "browsings")
            for browsing in self.browsings:
                ET.SubElement(self.doc, "browsing").text = browsing

        if self.container:
            self.doc = ET.SubElement(self.root, "container")
            for cont in self.container:
                ET.SubElement(self.doc, "veracrypt").text = cont

        if self.usermanagement:
            self.doc = ET.SubElement(self.root, "management")
            for cont in self.usermanagement:
                ET.SubElement(self.doc, "user").text = cont

        if self.registry:
            for cont in self.registry:
                ET.SubElement(self.doc, "registry").text = cont

        if self.filemanagement:
            self.doc = ET.SubElement(self.root, "filemanagement")
            for cont in self.filemanagement:
                ET.SubElement(self.doc, "filemanagement").text = cont

        if self.antiforensics:
            self.doc = ET.SubElement(self.root, "anti-forensics")
            for cont in self.antiforensics:
                ET.SubElement(self.doc, "anti-forensics").text = cont

        if self.chronological:
            self.doc = ET.SubElement(self.root, "chronological")
            for cont in self.chronological:
                ET.SubElement(self.doc, "chronological").text = cont

    def generate(self, export_path="./reports"):
        """
        Writing ElementTree (ET) to an XML file and changing rights to the file. This file can then be viewed
        with report.html.
        :return:
        """
        self.generateTags()
        tree = ET.ElementTree(self.root)
        tree.write(export_path + "report_" + self.imagename + "_" + self.date + ".xml")
        os.chmod(export_path + "report_" + self.imagename + "_" + self.date + ".xml", 0o777)
        self.logger.info("Report has been generated.")
