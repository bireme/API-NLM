#!/usr/bin/python3
# -*- coding: utf-8 -*-

#=========================================================================
#
#    Copyright © 2016 BIREME/PAHO/WHO
#
#    This file is part of API-NLM.
#
#    API-NLM is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 2.1 of
#    the License, or (at your option) any later version.
#
#    API-NLM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with API-NLM. If not, see <http://www.gnu.org/licenses/>.
#
#=========================================================================

import xml.etree.ElementTree as ET

class MyXML:
    def __init__(self,
                 xmlStr):
        """
        xmlStr - the xml string
        """
        self.xmlStr = xmlStr
        self.root = ET.Element("super_root")
        self.root.append(ET.fromstring(xmlStr))

    def getXPath(self,
                 xpath):
        """
        xpath - the xpath expression
        Returns a list of pairs with first element having the text of retrieved
        xml element and the second it attribute
        """
        ret = []
        xp = self.root.findall(xpath)
        for elem in xp:
            ret.append((elem.text, elem.attrib))

        return ret

    def getXPathElements(self,
                         xpath):
        """
        xpath - the xpath expression
        Returns a list of xml elements
        """
        #print("Element=" + str(self.root) + " xpath=" + xpath)
        xp = self.root.findall(xpath)
        #print("xp len=" + str(len(xp)))
        return xp

    def getXPathChildText(self,
                          father_xpath,
                          child_tags):
        """
        father_xpath - the xpath of the father xml element
        child_tags - the tags of the desired xml child elements
        Returns the text of desired children of a given xml element
        """
        ret = []
        fathers = self.root.findall(father_xpath)
        for father in fathers:
            text = []
            for tag in child_tags:
                txt = father.findtext(tag)
                if txt == None:
                    text.append("")
                else:
                    text.append(txt)
            ret.append(text)

        return ret

    def getTreeString(self,
                      element,
                      encoding="unicode"):
        """
        element - the root subtree element
        encoding - the encoding of the output string
        Returns a string having the tags, attributes and texts of all elements of
        a xml subtree
        """
        return ET.tostring(element, encoding)
