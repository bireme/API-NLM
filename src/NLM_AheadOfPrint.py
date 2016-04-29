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

from NLM_API import NLM_API
from MongoDb import MyMongo
from datetime import datetime

class NLM_AheadOfPrint:
    def __init__(self,
                 mongoHost,
                 dbName,
                 idColName,
                 xmlColName,
                 xmlOutDir,
                 encoding="UTF-8",
                 mongoPort=27017):
        """
        mongoHost - mongodb server host
        dbName - mongodb database name
        idColName - name of mongodb collection of ids
        xmlColName - name of mongodb collection of xmlRes
        xmlOutDir - directory path where xml files will be created
        encoding - xml files encoding
        mongoPort - mongodb server port
        """

        self.api = NLM_API()
        self.mid = MyMongo(dbName, idColName, mongoHost, mongoPort)
        self.mxml = MyMongo(dbName, xmlColName, mongoHost, mongoPort)
        self.dir = xmlOutDir
        self.encoding = encoding

        self.mid.createIndex("lastHarvesting", ["lastHarvesting"])

    def process(self,
                deletePublished=True,
                verbose=True):
        """
        Loads ahead of print xlm documents and saves then into mongo and files
        deletePublished - True if 'no more ahead of print' document should be
                          deleted from collection "xml"
        verbose - True if processing progress should be printed into standard
                  output
        """

        nowDate = datetime.now()
        numOfDocs = int(self.api.getDocIds(retmax=0)[0])
        retstart = 0
        loop = 1000 #10000


        # Insert new ahead of print documents
        while retstart < numOfDocs:
            idTuple = self.api.getDocIds(retmax=loop, retstart=retstart)
            self.api.insertDocs(nowDate, self.mid, self.mxml, idTuple[3],
                                self.dir, self.encoding, verbose)
            retstart += loop

        # Remove no more ahead of print documents
        self.api.changeDocStatus(nowDate, self.mid, self.mxml,
                                 delXmlDoc=deletePublished, verbose=verbose)

        elapsedTime = datetime.now() - nowDate
        print("\nElapsed time: " + str(elapsedTime))                         
