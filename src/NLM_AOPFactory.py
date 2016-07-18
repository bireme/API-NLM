#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =========================================================================
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
# =========================================================================


class NLM_AOPFactory:
    def __init__(self):
        self.myMongoId = None
        self.myMongoDoc = None
        self.xmlOutDir = None
        self.process = None
        self.owner = None
        self.encoding = "UTF-8"

    def setMyMongoId(self, myMongoId):
        """

        myMongoId - MyMongo object representing 'id' collection
        """
        self.myMongoId = myMongoId
        return self

    def setMyMongoDoc(self, myMongoDoc):
        """

        myMongoDoc - MyMongo object representing 'doc' collection
        """
        self.myMongoDoc = myMongoDoc
        return self

    def setXmlOutDir(self, xmlOutDir):
        """

        xmlOutDir - directory path where xml files will be created
        """
        self.xmlOutDir = xmlOutDir
        return self

    def setProcess(self, process):
        """

        process - harvesting process name
        """
        self.process = process
        return self

    def setOwner(self, owner):
        """

        owner - harvesting process owner
        """
        self.owner = owner
        return self

    def setEncoding(self, encoding):
        """

        encoding - xml files encoding
        """
        self.encoding = encoding
        return self

    def check(self):
        """
        Check if there is a missing parameter.

        """
        if self.myMongoId is None:
            raise Exception("myMongoId is None")
        if self.myMongoDoc is None:
            raise Exception("myMongoDoc is None")
        if self.xmlOutDir is None:
            raise Exception("xmlOutDir is None")
        if self.process is None:
            raise Exception("process is None")
        if self.owner is None:
            raise Exception("owner is None")
