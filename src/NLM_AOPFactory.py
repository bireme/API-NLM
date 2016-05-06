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

class NLM_AOPFactory:
    def __init__(self):
        self.mongoHost = None
        self.dbName = None
        self.idColName = None
        self.docColName = None
        self.xmlOutDir = None
        self.xmlProcDir = None
        self.date = None
        self.hour = None
        self.encoding = "UTF-8"
        self.mongoPort = 27017

    def setMongoHost(self, mongoHost):
        """
        mongoHost - mongodb server host
        """
        self.mongoHost = mongoHost
        return self

    def setMongoDbName(self, dbName):
        """
        dbName - mongodb database name
        """
        self.dbName = dbName
        return self

    def setMongoIdColName(self, idColName):
        """
        idColName - name of mongodb collection of ids
        """
        self.idColName = idColName
        return self

    def setMongoDocColName(self, docColName):
        """
        docColName - name of mongodb collection of documents
        """
        self.docColName = docColName
        return self

    def setXmlOutDir(self, xmlOutDir):
        """
        xmlOutDir - directory path where xml files will be created
        """
        self.xmlOutDir = xmlOutDir
        return self

    def setXmlProcDir(self, xmlProcDir):
        """
        xmlProcDir - directory path of xml files of standard medline processing
        """
        self.xmlProcDir = xmlProcDir
        return self

    def setDate(self, date):
        """
        date - current date string with format: YY-MM-DD
        """
        self.date = date
        return self

    def setHour(self, hour):
        """
        date - current time string with format: HH:MM:SS
        """
        self.hour = hour
        return self

    def setEncoding(self, encoding):
        """
        encoding - xml files encoding
        """
        self.encoding = encoding
        return self

    def setMongoPort(self, mongoPort):
        """
        mongoPort - mongodb server port
        """
        self.mongoPort = mongoPort
        return self

    def check(self):
        """
        Checks if there is a missing parameter
        """
        if self.mongoHost is None:
            raise Exception("mongoHost is None")
        if self.dbName is None:
            raise Exception("dbName is None")
        if self.idColName is None:
            raise Exception("idColName is None")
        if self.docColName is None:
            raise Exception("docColName is None")
        if self.xmlOutDir is None:
            raise Exception("xmlOutDir is None")
        if self.xmlProcDir is None:
            raise Exception("xmlProcDir is None")
        if self.date is None:
            raise Exception("date is None")
        if self.hour is None:
            raise Exception("hour is None")
