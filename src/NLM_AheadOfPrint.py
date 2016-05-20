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

from datetime import datetime
import fnmatch
import os
from os.path import join
import xmltodict
from NLM_API import NLM_API
from XML import MyXML
from DocIterator import DocIterator
import Tools

__date__ = 20160418


class NLM_AheadOfPrint:

    def __init__(self,
                 factory):
        """
        Constructor.

        mongoHost - mongodb server host
        factory - NLM_AOPFactory object
        """
        factory.check()

        self.api = NLM_API()
        self.mid = factory.myMongoId
        self.mdoc = factory.myMongoDoc
        self.xmlOutDir = factory.xmlOutDir
        self.xmlProcDir = factory.xmlProcDir
        self.encoding = factory.encoding
        self.process_ = factory.process
        self.owner = factory.owner

    def __insertDocId(self,
                      docId,
                      dateBegin,
                      hourBegin):
        """
        Insert an id document into collection "id".

        docId - NLM document id
        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        Returns True is it a new document False is it was already saved
        """
        # Document is new if it is not in id collection or if its status is
        # 'in process' meaning that a previous download was unfinished.
        query = {"id": docId, "status": {"$ne": "in process"}}
        cursor = self.mid.search(query)
        isNew = (cursor.count() == 0)

        if isNew:
            doc = {"id": docId}
            doc["date"] = dateBegin
            doc["hour"] = hourBegin
            doc["status"] = "in process"
            doc["process"] = self.process_
            doc["owner"] = self.owner
            self.mid.saveDoc(doc)  # Save document into mongo
        else:
            # If document is not new and its status is not ahead of print
            # status='no_aheadofprint' or status='moved',
            # delete the physical file and from doc collection.
            oldDoc = cursor[0]
            if oldDoc["status"] != 'aheadofprint':
                fpath = join(self.xmlOutDir, docId + ".xml")
                if Tools.existFile(fpath):
                    try:
                        Tools.removeFile(fpath)
                    except OSError:
                        raise Exception("Document id:" + str(docId) +
                                        " deletion failed")
                self.mdoc.deleteDoc(docId)

        return isNew

    def __insertDocs(self,
                     ids,
                     dateBegin,
                     hourBegin,
                     xdir=".",
                     encoding="UTF-8",
                     verbose=False):
        """
        For each id from a list of ids, adds a new id document into mongo id
        collection, add a new document into mongo xml collection and creates a
        new file with xml content.

        ids - a list of NLM document ids
        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        xdir - output file directory
        encoding - output file encoding
        verbose - if True prints the document is inserted
        """
        newDocs = []
        id_size = len(ids)
        # print("dateBegin=" + dateBegin)
        if verbose:
            print("Checking " + str(id_size) + " documents: ",
                  end='', flush=True)
        for id_ in ids:
            # Insert id document into collection "id"
            isNewDoc = self.__insertDocId(id_, dateBegin, hourBegin)
            if isNewDoc:
                newDocs.append(id_)
            if verbose:
                ch = '+' if isNewDoc else '.'
                print(ch, end='', flush=True)

        newDocLen = len(newDocs)
        if newDocLen > 0:
            if verbose:
                print("\nDownloading and saving " + str(newDocLen) +
                      " documents: ", end='', flush=True)
            diter = DocIterator(newDocs, verbose=verbose)

            for dId in diter:
                docId = dId[0]
                xml = dId[1]

                # Save xml content into mongo and file
                Tools.xmlToFile(docId, xml, xdir, encoding)  # save into file
                docDict = xmltodict.parse(xml)
                doc = {"_id": docId, "doc": docDict}
                self.mdoc.saveDoc(doc)  # save into mongo 'doc' collection

                # Change document document status from 'in process' to
                # 'aheadofprint' in id collection.
                doc = self.mid.search({"id": docId})[0]
                doc["status"] = "aheadofprint"
                self.mid.replaceDoc(doc)   # save into mongo 'id' collection

            if verbose:
                print()  # to print a new line

    def __changeDocStatus(self,
                          ids,
                          dateBegin,
                          hourBegin,
                          verbose=False):
        """
        Change the document status from "aheadofprint/moved" to
        "no_aheadofprint" if MongoDb lastHarvesting document field is not
        in the ids list.

        ids - list of aheadofprint document ids
        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        verbose - if True prints document id into standard output
        """
        # Searches all documents in the 'doc' collection that belongs to the
        # ids list. If document is not in the list, delete it.
        query = {"_id": {"$nin": ids}}
        cursor = self.mdoc.search(query)

        for oldDoc in cursor:
            id_ = oldDoc["_id"]
            # Deletes the xml physical file
            fpath = join(self.xmlOutDir, id_ + ".xml")
            try:
                Tools.removeFile(fpath)
            except OSError:
                pass

            # Deletes document from 'doc' collection
            self.mdoc.deleteDoc(id_)

            # Update id mongo doc
            doc = {"id": id_}
            doc["date"] = dateBegin
            doc["hour"] = hourBegin
            doc["status"] = "no_aheadofprint"
            doc["process"] = self.process_
            doc["owner"] = self.owner
            self.mid.saveDoc(doc)
        if verbose:
            print("Total: " + str(cursor.count()) + " xml files were deleted.")

    def __getDocIdList(self,
                       filePath,
                       idXPath="MedlineCitationSet/MedlineCitation/PMID",
                       encoding="UTF-8"):
        """

        filePath - the xml file path
        idXPath - the xml path to the document id
        encoding - xml file encoding
        Returns a list of id tags of a xml document.
        """
        ids = []
        xml = Tools.readFile(filePath, encoding=encoding)
        xpath = MyXML(xml)
        xlist = xpath.getXPath(idXPath)

        for elem in xlist:
            ids.append(elem[0])

        return ids

    def __changeDocStatus2(self,
                           dateBegin,
                           hourBegin,
                           fileFilter="*",
                           verbose=False):
        """
        Change the document status from "aheadofprint" to "no_aheadofprint" if
        the xml document id is also present in 'workDir'
        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        fileFilter - Unix shell-style wildcards for file filtering
        verbose - if True prints document id into standard output
        """
        removed = 0  # Removed xml files

        # For all documents in medline processing directory
        listDir = os.listdir(self.xmlProcDir)
        for f in listDir:
            if verbose:
                print(".", end='', flush=True)

            # Searches if there is a mongo document with same id and
            # updates/deletes it.
            if fnmatch.fnmatch(f, fileFilter):
                # Get the xml doc id from file
                idList = self.__getDocIdList(join(self.xmlProcDir, f))
                for id_ in idList:
                    # If there is such document
                    query = {"_id": id_}
                    cursor = self.mdoc.search(query)
                    if cursor.count() > 0:
                        # Delete xml physical file
                        filename = join(self.xmlOutDir, id_ + ".xml")
                        try:
                            os.remove(filename)
                        except OSError:
                            pass

                        # Delete document from mongo doc collection
                        self.mdoc.deleteDoc(id_)

                        # Update document status from mongo id collection
                        doc = {"id": id_}
                        doc["date"] = dateBegin
                        doc["hour"] = hourBegin
                        doc["status"] = "no_aheadofprint"
                        doc["process"] = self.process_
                        doc["owner"] = self.owner
                        self.mid.saveDoc(doc)    # create new id mongo doc
                        removed += 1

        if verbose:
            print("\nTotal: " + str(removed) + " xml files were deleted.")

    def process(self,
                dateBegin,
                hourBegin,
                verbose=True):
        """
        Download 'ahead of print' xlm documents and saves then into mongo
                  and files.

        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
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
            print("\nRemoving no ahead of print documents.", flush=True)
        self.__changeDocStatus(idList, dateBegin, hourBegin, verbose)

        # Insert new ahead of print documents
        from_ = 0
        loop = 1000  # 10000

        while from_ < numOfDocs:
            if verbose:
                print("\n" + str(from_+1) + "/" + str(numOfDocs))

            to = from_ + loop
            self.__insertDocs(idList[from_:to],
                              dateBegin, hourBegin,
                              self.xmlOutDir, self.encoding, verbose)
            from_ += loop

        if verbose:
            elapsedTime = datetime.now() - nowDate
            print("\nElapsed time: " + str(elapsedTime))

    def syncWorkDir(self,
                    dateBegin,
                    hourBegin,
                    verbose=True):
        """
        Remove from processing directory all documents which are also in the
        xmlProcDir. After that, moves all documents from download directory
        into xmlProcDir.

        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        verbose - True if processing progress should be printed into standard
                  output
        """
        nowDate = datetime.now()

        # Removes duplicated documents from processing directory and workDir
        if verbose:
            print("\nRemoving duplicated xml files: ", end="", flush=True)
        self.__changeDocStatus2(dateBegin, hourBegin, "medline*.xml", verbose)

        # Copies all xml files to the oficial processing directory
        if verbose:
            print("\nMoving xml files to the processing directory: ",
                  flush=True)

        #  For all documents in download dir
        listDir = os.listdir(self.xmlOutDir)

        for f in listDir:
            if verbose:
                print(".", end="", flush=True)

            if fnmatch.fnmatch(f, "*.xml"):
                idList = self.__getDocIdList(join(self.xmlOutDir, f))
                if len(idList) == 0:
                    if verbose:
                        print("id from xml file [" + str(f) +
                              "] was not found.")
                else:  # If there is such document
                    id_ = idList[0]
                    query = {"id": id_, "status": "aheadofprint"}
                    cursor = self.mid.search(query)
                    if cursor.count() > 0:
                        # Move xml physical file
                        filename = id_ + ".xml"
                        try:
                            Tools.moveFile(self.xmlOutDir, self.xmlProcDir,
                                           filename, createToDir=False)
                        except OSError:
                            pass

                        # Update document status from mongo id collection
                        doc = {"id": id_}
                        doc["date"] = dateBegin
                        doc["hour"] = hourBegin
                        doc["status"] = "moved"
                        doc["process"] = self.process_
                        doc["owner"] = self.owner
                        self.mid.saveDoc(doc)    # create new id mongo doc

        if verbose:
            elapsedTime = datetime.now() - nowDate
            print("\n\nElapsed time: " + str(elapsedTime))
