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
from LogDocument import LogDocument
from NLM_API import NLM_API
from XML import MyXML
from DocIterator import DocIterator
import Tools

__date__ = 20160418


class NLM_AheadOfPrint:

    def __init__(self,
                 factory):
        """

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
        self.logDocument = LogDocument(factory.date, factory.hour,
                                       factory.process, factory.owner)

    def __insertDocId(self,
                      docId):
        """
            Inserts an id document into collection "id".

            docId - NLM document id
            Returns True is it a new document False is it was already saved
        """

        query = {"_id": docId}

        # Check if the new document is already stored in Mongo and
        # physical file
        cursor = self.mdoc.search(query)

        isNew = (cursor.count() == 0)
        # print("isNew1=" + str(isNew))
        if not isNew:
            # print("arquivo: " + join(self.xmlOutDir, docId + ".xml"))
            # Last processing failed
            isNew = not Tools.existFile(join(self.xmlOutDir, docId + ".xml"))
            # print("isNew2=" + str(isNew))
            if isNew:
                # print("antes da delecao:" + docId)
                # Forces mongo xml document delete
                if not self.mdoc.deleteDoc(docId):
                    raise Exception("Document id:" + str(docId) +
                                    " deletion failed")

        if isNew:
            doc = self.logDocument.getNewDoc(docId, "aheadofprint")
            self.mid.saveDoc(doc)  # Save document into mongo

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
            print("Checking " + str(id_size) + " documents: ",
                   end='', flush=True)
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
                self.mdoc.saveDoc(doc)                       # save into mongo

            if verbose:
                print()  # to print a new line

    def __changeDocStatus(self,
                          ids,
                          verbose=False):
        """
        Change the document status from "aheadofprint" to "no_aheadofprint" if
        MongoDb lastHarvesting document field is not in the ids list.

        ids - list of aheadofprint document ids
        verbose - if True prints document id into standard output
        """
        # Searches all documents in the doc collection belongs to the ids list.
        # if not delete it.
        query = {"_id": {"$nin": ids}}
        cursor = self.mdoc.search(query)

        for oldDoc in cursor:
            id_ = oldDoc["_id"]

            # Update id mongo doc
            self.mid.saveDoc(doc=self.logDocument.getNewDoc(id_,
                                                            "no_aheadofprint"))

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
                   idXPath="MedlineCitationSet/MedlineCitation/PMID",
                   encoding="UTF-8"):
        """

        filePath - the xml file path
        idXPath - the xml path to the document id
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
                           fileFilter="*",
                           verbose=False):
        """
        Changes the document status from "aheadofprint" to "no_aheadofprint" if
        the xml document id is also present in 'workDir'
        workDir - directory in where the xml files will be searched
        fileFilter - Unix shell-style wildcards for file filtering
        verbose - if True prints document id into standard output
        """
        # For all documents in workDir
        listDir = os.listdir(workDir)

        for f in listDir:
            # Searches if there is a mongo document with same id and
            # updates/deletes it.
            if fnmatch.fnmatch(f, fileFilter):
                id_ = self.__getDocId(join(workDir, f))
                if id_ is None:
                    if verbose:
                        print("id from xml file [" + str(f) +
                              "] was not found.")
                else:
                    query = {"_id": id_}
                    cursor = self.mdoc.search(query)

                    if cursor.count() > 0:
                        doc = self.logDocument.getNewDoc(id_,
                                                         "no_aheadofprint")

                        self.mid.saveDoc(doc)    # create new id mongo doc

                        # Delete xml physical file
                        filename = join(self.xmlOutDir, id_ + ".xml")
                        try:
                            os.remove(filename)
                        except OSError:
                            pass

                        self.mdoc.deleteDoc(id_)  # delete xml mongo doc

        if verbose:
            print("Total: " + str(len(listDir)) + " xml files were deleted.")

    def process(self,
                verbose=True):
        """
        Download 'ahead of print' xlm documents and saves then into mongo
                   and files.

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
        self.__changeDocStatus(idList, verbose)

        # Insert new ahead of print documents
        from_ = 0
        loop = 1000  # 10000

        while from_ < numOfDocs:
            if verbose:
                print("\n" + str(from_+1) + "/" + str(numOfDocs))

            to = from_ + loop
            self.__insertDocs(idList[from_:to], self.xmlOutDir,
                              self.encoding, verbose)
            from_ += loop

        if verbose:
            elapsedTime = datetime.now() - nowDate
            print("\nElapsed time: " + str(elapsedTime))

    def syncWorkDir(self,
                    verbose=True):
        """
        Remove from processing directory all documents which are also in the
        xmlProcDir. After that, moves all documents from processing directory
        into xmlProcDir.

        """
        nowDate = datetime.now()

        # Removes duplicated documents from processing directory and workDir
        if verbose:
            print("\nRemoving duplicated xml files.", flush=True)
        self.__changeDocStatus2(self.xmlProcDir, "medline*.xml", verbose)

        # Copies all xml files to the oficial processing directory
        if verbose:
            print("\nMoving xml files to the processing directory.",
                  flush=True)
        Tools.moveFiles(self.xmlOutDir, self.xmlProcDir, fileFilter="*.xml",
                        createToDir=False)

        if verbose:
            elapsedTime = datetime.now() - nowDate
            print("\nElapsed time: " + str(elapsedTime))
