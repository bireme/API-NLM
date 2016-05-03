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
from DocIterator import DocIterator
from datetime import datetime
from os.path import exists
import Tools
import xmltodict

__date__ = 20160418

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

        self.dir = xmlOutDir.strip()
        if not self.dir.endswith("/"): self.dir += "/"

        self.encoding = encoding
        self.mid.createIndex("lastHarvesting", ["lastHarvesting"])
        self.mid.createIndex("status", ["_id", "status"])


    def __insertDocId(self,
                      nowDate,
                      docId):
        """
            Inserts an id document into collection "id"
            nowDate - current date
            docId - NLM document id
            Returns True is it a new document False is it was already saved
        """

        doc = {"_id":docId}

        # Check if the new document is already stored in Mongo and physical file
        cursor = self.mid.search(doc)
        isNew = (cursor.count() == 0)
        if isNew:
            doc["firstHarvesting"] = nowDate
            doc["status"] = "aheadofprint"
        else:
            doc = cursor[0]
            if (doc["status"] == "aheadofprint"):
                if (not exists(self.dir + docId + ".xml")): # last processing failed
                    isNew = True # Re-process this document
                else:
                    doc["firstHarvesting"] = nowDate

        doc["lastHarvesting"] = nowDate

        # Update id onto mongo
        self.mid.replaceDoc(doc)

        return isNew


    def __insertDocs(self,
                     nowDate,
                     ids,
                     xdir=".",
                     encoding="UTF-8",
                     verbose=False):
        """
        For each id from a list of ids, adds a new id document into mongo id
        collection, add a new document into mongo xml collection and creates a
        new file with xml content.
        nowDate - current date
        ids - a list of NLM document ids
        xdir - output file directory
        encoding - output file encoding
        verbose - if True prints the document is inserted
        """

        newDocs = []
        id_size = len(ids)

        for id_ in ids:
            # Insert id document into collection "id"
            isNewDoc = self.__insertDocId(nowDate, id_)
            if isNewDoc:
                newDocs.append(id_)
            if (verbose):
                status = "[New]" if isNewDoc else "[Already processed]"
                print("Document id:" + str(id_) + " " + status)

        if len(newDocs) > 0:
            if verbose:
                print("Downloading and saving " + str(id_size) + " documents: ",
                                                             end='', flush=True)
            diter = DocIterator(newDocs, verbose=verbose)

            for dId in diter:
                docId = dId[0]
                xml = dId[1]

                # Save xml content into mongo and file
                docDict = xmltodict.parse(xml)
                doc = {"_id":docId, "date":nowDate, "doc":docDict}
                self.mxml.saveDoc(doc)                      # save into mongo
                Tools.xmlToFile(docId, xml, xdir, encoding)    # save into file

            if verbose:
                print()  # to print a new line


    def __changeDocStatus(self,
                          nowDate,
                          verbose=False):
        """
        Changes the document status from "aheadofprint" to "no_aheadofprint" if
        MongoDb lastHarvesting document field is older than 'nowDate'.
        nowDate - current date
        verbose - if True prints document id into standard output
        """

        # Searchs all documents whose lastHarvesting is lower than nowDate
        query = {"lt":{"lastHarvesting":nowDate}}
        cursor = self.mid.search(query)

        for doc in cursor:
            doc.lastHarvesting = nowDate
            doc.status = "no_aheadofprint"

            self.mid.replaceDoc(doc) # update id mongo doc

            id_ = doc._id

            # Deletes document from collection "xml"
            self.mxml.deleteDoc(id_)

            # Deletes the xml physical file
            xdir = self.dir + id_ + ".xml"
            try:
                os.remove(filename)
            except OSError:
                pass

            if verbose:
                print("Doc[" + id_ + "] status changed. Xml deleted.")


    def __getDocId(filePath,
                   idXPath="PubmedArticle/MedlineCitation/PMID",
                   encoding="UFT-8"):
        """
        filePath - the xml file path
        encoding - xml file encoding
        Returns the id tag of a xml document.
        """
        xml = readFile(filePath,encoding=encoding)
        xpath = MyXML(xml)
        list = xpath(idXPath)

        if len(list) == 0:
            id = None
        else:
            id = list[0][0]

        return id


    def __changeDocStatus2(self,
                           workDir,
                           verbose=False):
        """
        Changes the document status from "aheadofprint" to "no_aheadofprint" if
        the xml document is also present in 'workDir'
        workDir - directory in where the xml files will be searched
        verbose - if True prints document id into standard output
        """

        # For all documents in workDir
        for f in listdir(workDir):
            id = __getDocId(join(workDir, f))

            # Searches if there is a mongo document with same id and updates/deletes it.
            query = {"_id": id, "status":"aheadofprint"}
            cursor = self.mid.search(query)
            for doc in cursor:
                doc.lastHarvesting = nowDate
                doc.status = "no_aheadofprint"

                self.mid.replaceDoc(doc) # update id mongo doc
                self.mxml.deleteDoc(id)   # delete xml mongo doc

                xdir = self.dir + id_ + ".xml" # delete xml physical file
                try:
                    os.remove(filename)
                except OSError:
                    pass

                if verbose:
                    print("Doc[" + id_ + "] status changed. Xml deleted.")


    def process(self,
                verbose=True):
        """
        Downloads 'ahead of print' xlm documents and saves then into mongo and files
        verbose - True if processing progress should be printed into standard
                  output
        """

        nowDate = datetime.now()
        numOfDocs = int(self.api.getDocIds(retmax=0)[0])
        retstart = 0
        loop = 1000 #10000

        # Insert new ahead of print documents
        while retstart < numOfDocs:
            if verbose:
                print("\n" + str(retstart+1) + "/" + str(numOfDocs))

            idTuple = self.api.getDocIds(retmax=loop, retstart=retstart)
            self.__insertDocs(nowDate, idTuple[3], self.dir, self.encoding,
                                                                        verbose)
            retstart += loop

        # Remove no more ahead of print documents
        self.__changeDocStatus(nowDate, self.mid, self.mxml, verbose=verbose)

        elapsedTime = datetime.now() - nowDate
        print("\nElapsed time: " + str(elapsedTime))


    def syncWorkDir(self,
                    workDir,
                    verbose=True):
        """
        Removes from processing directory all documents which are also in the
        workDir. After that, moves all documents from processing directory into
        workDir.
        workDir - directory into which the NLM documents with no_aheadofprint
                  status were downloaded.
        """
        nowDate = datetime.now()

        # Removes duplicated documents from processing directory and workDir
        self.__changeDocStatus2(workDir, verbose)

        # Moves all xml files from processing directory to workDir directory
        Tools.moveFiles(self.dir, workDir, fileFilter="*.xml", createToDir=False)

        elapsedTime = datetime.now() - nowDate
        print("\nElapsed time: " + str(elapsedTime))
