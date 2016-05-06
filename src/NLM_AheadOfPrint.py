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

from datetime import datetime
import os
from os.path import join
import xmltodict
from NLM_API import NLM_API
from MongoDb import MyMongo
from XML import MyXML
from DocIterator import DocIterator
import Tools

__date__ = 20160418

class NLM_AheadOfPrint:
    def __init__(self,
                 factory):
        """
        mongoHost - mongodb server host
        dbName - mongodb database name
        idColName - name of mongodb collection of ids
        docColName - name of mongodb collection of documents
        xmlOutDir - directory path where xml files will be created
        nowDate - current date/time
        encoding - xml files encoding
        mongoPort - mongodb server port
        """

        factory.check()

        self.api = NLM_API()
        self.mid = MyMongo(factory.dbName, factory.idColName, factory.mongoHost,
                           factory.mongoPort)
        self.mdoc = MyMongo(factory.dbName, factory.docColName,
                            factory.mongoHost, factory.mongoPort)

        self.xmlOutDir = factory.xmlOutDir
        self.xmlProcDir = factory.xmlProcDir
        self.date = factory.date
        self.hour = factory.hour
        self.encoding = factory.encoding


    def __getNewDoc(self,
                    id_,
                    status="aheadofprint"):
        """
        id_ - document id
        status - document status: aheadofprint or no_aheadofprint
        Returns a new document
        """
        doc = {"id": id_}
        doc["data"] = self.date
        doc["hour"] = self.hour
        doc["process"] = "api-nlm"
        doc["status"] = status
        doc["owner"] = "unknown"

        return doc

    def insert(self, docId):
        return self.__insertDocId(docId)

    def __insertDocId(self,
                      docId):
        """
            Inserts an id document into collection "id"
            docId - NLM document id
            Returns True is it a new document False is it was already saved
        """

        query = {"_id": docId}

        # Check if the new document is already stored in Mongo and physical file
        cursor = self.mdoc.search(query)

        isNew = (cursor.count() == 0)
        #print("isNew1=" + str(isNew))
        if not isNew:
            #print("arquivo: " + join(self.xmlOutDir, docId + ".xml"))
             # Last processing failed
            isNew = not Tools.existFile(join(self.xmlOutDir, docId + ".xml"))
            #print("isNew2=" + str(isNew))
            if isNew:
                #print("antes da delecao:" + docId)
                if not self.mdoc.deleteDoc(docId):  # forces mongo xml document delete
                    raise Exception("Document id:" + str(docId) + " deletion failed")

        if isNew:
            doc = self.__getNewDoc(docId)
            self.mid.saveDoc(doc) # Save document into mongo

        return isNew


    def __insertDocs(self,
                     ids,
                     xdir=".",
                     encoding="UTF-8",
                     verbose=False):
        """
        For each id from a list of ids, adds a new id document into mongo id
        collection, add a new document into mongo xml collection and creates a
        new file with xml content.
        ids - a list of NLM document ids
        xdir - output file directory
        encoding - output file encoding
        verbose - if True prints the document is inserted
        """

        newDocs = []
        id_size = len(ids)

        if verbose:
            print("Checking " + str(id_size) + " documents: ", end='', flush=True)
        for id_ in ids:
            # Insert id document into collection "id"
            isNewDoc = self.__insertDocId(id_)
            if isNewDoc:
                newDocs.append(id_)
            if verbose:
                ch = '+' if isNewDoc else '.'
                print(ch, end='', flush=True)

        newDocLen = len(newDocs)
        if newDocLen > 0:
            if verbose:
                print("\nDownloading and saving " + str(newDocLen) + " documents: ",
                      end='', flush=True)
            diter = DocIterator(newDocs, verbose=verbose)

            for dId in diter:
                docId = dId[0]
                xml = dId[1]

                # Save xml content into mongo and file
                Tools.xmlToFile(docId, xml, xdir, encoding)    # save into file
                docDict = xmltodict.parse(xml)
                doc = {"_id":docId, "doc":docDict}
                self.mdoc.saveDoc(doc)                         # save into mongo

            if verbose:
                print()  # to print a new line


    def __changeDocStatus(self,
                          ids,
                          verbose=False):
        """
        Changes the document status from "aheadofprint" to "no_aheadofprint" if
        MongoDb lastHarvesting document field is older than current date/hour.
        ids - list of aheadofprint document ids
        verbose - if True prints document id into standard output
        """

        # Searches all documents in the doc collection belongs to the ids list.
        # if not delete it.
        query = {"_id" : {"$nin" : ids}}
        cursor = self.mdoc.search(query)

        for oldDoc in cursor:
            id_ = oldDoc["_id"]

            # Update id mongo doc
            self.mid.saveDoc(self.__getNewDoc(id_, "no_aheadofprint"))

            # Deletes the xml physical file
            fpath = join(self.xmlOutDir, id_ + ".xml")
            try:
                Tools.removeFile(fpath)
            except OSError:
                pass

            # Deletes document from collection "xml"
            self.mdoc.deleteDoc(id_)

        if verbose:
            print("Total: " + str(cursor.count()) + " xml files were deleted.")


    def __getDocId(self,
                   filePath,
                   idXPath="PubmedArticle/MedlineCitation/PMID",
                   encoding="UFT-8"):
        """
        filePath - the xml file path
        encoding - xml file encoding
        Returns the id tag of a xml document.
        """
        xml = Tools.readFile(filePath, encoding=encoding)
        xpath = MyXML(xml)
        xlist = xpath.getXPath(idXPath)

        if len(xlist) == 0:
            id_ = None
        else:
            id_ = xlist[0][0]

        return id_


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
        for f in os.listdir(workDir):
            id_ = self.__getDocId(join(workDir, f))

            # Searches if there is a mongo document with same id and updates/deletes it.
            query = {"_id": id}
            cursor = self.mdoc.search(query)

            if len(cursor > 0):
                doc = self.__getNewDoc(id, "no_aheadofprint")

                self.mid.saveDoc(doc)    # create new id mongo doc

                filename = join(self.xmlOutDir, id_ + ".xml") # delete xml physical file
                try:
                    os.remove(filename)
                except OSError:
                    pass

                self.mdoc.deleteDoc(id)  # delete xml mongo doc

                if verbose:
                    print("Doc[" + id + "] status changed. Xml deleted.")


    def process(self,
                verbose=True):
        """
        Downloads 'ahead of print' xlm documents and saves then into mongo and files
        verbose - True if processing progress should be printed into standard
                  output
        """

        nowDate = datetime.now()

        # Retrive all ahead of print document ids
        if verbose:
            print("\nRetrieving document ids: ", end='')

        idTuple = self.api.getAllIds()
        numOfDocs = int(idTuple[0])
        idList = idTuple[1]

        if verbose:
            print("Total: " + str(numOfDocs) + " ahead of print documents.",
                  flush=True)

        # Remove no more ahead of print documents
        if verbose:
            print("\nRemoving no ahead of print documents.")
        self.__changeDocStatus(idList, verbose)

        # Insert new ahead of print documents
        from_ = 0
        loop = 1000 #10000

        while from_ < numOfDocs:
            if verbose:
                print("\n" + str(from_+1) + "/" + str(numOfDocs))

            to = from_ + loop
            self.__insertDocs(idList[from_:to], self.xmlOutDir, self.encoding, verbose)
            from_ += loop

        if verbose:
            elapsedTime = datetime.now() - nowDate
            print("\nElapsed time: " + str(elapsedTime))


    def syncWorkDir(self,
                    verbose=True):
        """
        Removes from processing directory all documents which are also in the
        xmlProcDir. After that, moves all documents from processing directory
        into xmlProcDir.
        """
        nowDate = datetime.now()

        # Removes duplicated documents from processing directory and workDir
        self.__changeDocStatus2(self.xmlProcDir, verbose)

        # Moves all xml files from processing directory to workDir directory
        Tools.moveFiles(self.xmlOutDir, self.xmlProcDir, fileFilter="*.xml",
                        createToDir=False)

        if verbose:
            elapsedTime = datetime.now() - nowDate
            print("\nElapsed time: " + str(elapsedTime))
