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
from os.path import join
import xmltodict
from NLM_API import NLM_API
from RegularExpression import RegularExpression
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
        self.encoding = factory.encoding
        self.process_ = factory.process
        self.owner = factory.owner

        self.mid.createIndex("id", ["id"])
        self.mid.createIndex("id_status", ["id", "status"])
        self.mid.createIndex("date_hour_status", ["date", "hour", "status"])

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
        doc = self.mid.searchOne({"id": docId})
        if doc is None:
            isNew = True
            doc = {"_id": docId}
            doc["id"] = docId
            doc["date"] = dateBegin
            doc["hour"] = hourBegin
            doc["status"] = "in process"
            doc["process"] = self.process_
            doc["owner"] = self.owner
            self.mid.bulkInsertDoc(doc)  # Save document into mongo
        else:
            if doc["status"] is "in process":
                isNew = True
                fpath = join(self.xmlOutDir, docId + ".xml")
                if Tools.existFile(fpath):
                    try:
                        Tools.removeFile(fpath)
                    except OSError:
                        raise Exception("Document id:" + str(docId) +
                                        " deletion failed")
                self.mdoc.deleteDoc(docId)

            else:  # aheadofprint, no_aheadofprint
                isNew = False

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

        bulkCount = 0
        notWrittenDocs = 0
        bulkRemaining = False
        # print("\nNumero de ids baixados: " + str(id_size))
        for id_ in ids:
            # Insert id document into collection "id"
            isNewDoc = self.__insertDocId(id_, dateBegin, hourBegin)
            if isNewDoc:
                newDocs.append(id_)
                bulkCount += 1
                bulkRemaining = True
                if bulkCount % 100 == 0:
                    self.mid.bulkWrite()
                    bulkRemaining = False
            else:
                notWrittenDocs += 1

            if verbose:
                ch = '+' if isNewDoc else '.'
                print(ch, end='', flush=True)

        # Write remaining
        if bulkRemaining:
            self.mid.bulkWrite()
            bulkRemaining = False

        if ((bulkCount + notWrittenDocs) != id_size):
            raise Exception("__insertDocs: some doc ids were not written")

        newDocLen = len(newDocs)
        # print("\nNumero de ids novos: " + str(newDocLen))
        if newDocLen > 0:
            if verbose:
                print("\nDownloading and saving " + str(newDocLen) +
                      " documents: ", end='', flush=True)
            diter = DocIterator(newDocs, verbose=verbose)

            bulkCount = 0
            bulkRemaining = False

            for dId in diter:
                docId = dId[0]
                xml = dId[1]

                # Save xml content into mongo and file
                Tools.xmlToFile(docId, xml, xdir, encoding)  # save into file
                docDict = xmltodict.parse(xml)
                doc = {"_id": docId, "doc": docDict}
                self.mdoc.bulkInsertDoc(doc)  # save into mongo 'doc' coll

                # Change document document status from 'in process' to
                # 'aheadofprint' in id collection.
                self.mid.bulkUpdateDoc({"id": docId},
                                       {"status": "aheadofprint"})

                bulkRemaining = True
                bulkCount += 1
                if bulkCount % 100 == 0:
                    self.mid.bulkWrite()
                    self.mdoc.bulkWrite()
                    bulkRemaining = False

            # Write remaining
            if bulkRemaining:
                self.mid.bulkWrite()
                self.mdoc.bulkWrite()

            if bulkCount != newDocLen:
                raise Exception("__insertDocs: some new docs were not written")

            # print("\nDocumentos escritos: " + str(bulkCount))
            if verbose:
                print()  # to print a new line

    def __checkInProcess(self):
        """Check if there are documents with "in process" status."""
        query = {"status": "in process"}
        cursor = self.mid.search(query)

        return cursor.count() > 0

    def __changeDocStatus(self,
                          ids,
                          dateBegin,
                          hourBegin,
                          verbose=False):
        """
        Change the document status from "aheadofprint" to
        "no_aheadofprint" if MongoDb lastHarvesting document field is not
        in the ids list.
        ids - list of aheadofprint document ids
        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        verbose - if True prints document id into standard output
        """
        # Searches all documents in the 'doc' collection that belongs to the
        # ids list. If document is not in the list and is aheadofprint,
        # delete it.
        query = {"id": {"$nin": ids}, "status": "aheadofprint"}
        cursor = self.mid.search(query)
        tot = cursor.count()

        for oldDoc in cursor:
            id_ = oldDoc["id"]
            # Deletes the xml physical file
            fpath = join(self.xmlOutDir, id_ + ".xml")
            try:
                Tools.removeFile(fpath)
            except OSError:
                raise Exception("Remove file [" + str(fpath) + "] error")

            # Deletes document from 'doc' collection
            self.mdoc.deleteDoc(id_)

            # Update id mongo doc
            doc = {"_id": oldDoc["_id"]}
            doc["id"] = id_
            doc["date"] = dateBegin
            doc["hour"] = hourBegin
            doc["status"] = "no_aheadofprint"
            doc["process"] = self.process_
            doc["owner"] = self.owner
            self.mid.replaceDoc(doc)
        if verbose:
            print("Total: " + str(tot) + " xml files were deleted.")

    def __getDocIdList(self,
                       filePath,
                       regExp,
                       encoding="UTF-8"):
        """

        filePath - the xml file path
        regExp - the regular expression used to extract the document id
        encoding - xml file encoding
        Returns a list of id tags from a xml document.
        """
        xml = Tools.readFile(filePath, encoding=encoding)
        rex = RegularExpression(regExp, dotAll=True)

        return rex.findAll(xml)

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
