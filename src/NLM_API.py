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

from LoadUrl import loadUrl
from XML import MyXML
from MongoDb import MyMongo
from DocIterator import DocIterator
import json,xmltodict,os

class NLM_API:
    def __init__(self):
        self.eutils = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils"


    def listDatabases(self):
        """
        Lists the databases that can be used by eutils api
        Returns a list of database names
        """
        databases = []

        xmlRes = loadUrl(self.eutils + "/einfo.fcgi")
        if xmlRes[0] == 200:
            xml = MyXML(xmlRes[1])
            xpath = xml.getXPath("eInfoResult/DbList/DbName")

            for xp in xpath:
                databases.append(xp[0])

        return databases


    def listDatabaseFields(self, dbname):
        """
        Lists the fields of a database
        dbname - the database name
        Returns a list of field names
        """
        info = []
        xmlRes = loadUrl(self.eutils + "/einfo.fcgi?db=" + dbname + "&version=2.0")

        if xmlRes[0] == 200:
            xml = MyXML(xmlRes[1])
            info = xml.getXPathChildText("eInfoResult/DbInfo/FieldList/Field", ['Name', 'FullName', 'Description'])

        return info


    def getDocIds(self,
                  dbname="pubmed",
                  query="pubstatusaheadofprint",
                  retmax=1000,
                  retstart=0,
                  field=None,
                  useHistory=False):
        """
        dbname - database name
        query - expression used to retrieve the document ids
        retmax - the maximum number of returned ids
        retstart - initial position (from id list) used to return ids
        field - if used narrow the search to that field
        useHistory - true if the retrieved ids should the stored in the server
                     for temporary and future use by efetch.
        Returns a tuple as follows:
               (<#ofIds>, <webenv>, <querykey>, <list of the document ids that are retrieved by a query>)
        """
        url = self.eutils + "/esearch.fcgi?db=" + dbname + "&term=" + query \
                + "&retstart=" + str(retstart)

        if (useHistory):
            url = url + "&usehistory=y"
            retmax = 0
        if (field != None):
            url = url + "&field=" + field

        url = url + "&retmax=" + str(retmax)

        count = 0
        web = ""
        key = ""
        ids = []

        xmlRes = loadUrl(url)
        if xmlRes[0] == 200:
            xml = MyXML(xmlRes[1])
            count = xml.getXPath("eSearchResult/Count")[0][0]
            #print("count=" + str(count))
            if (useHistory):
                web = xml.getXPath("eSearchResult/WebEnv")[0][0]
                key = xml.getXPath("eSearchResult/QueryKey")[0][0]

            if (retmax > 0):
                id_list = xml.getXPath("eSearchResult/IdList/Id")
                for id in id_list:
                    ids.append(id[0])

        return (count, web, key, ids)


    def __insertDocId(self,
                      idMyMongo,
                      nowDate,
                      docId):
        """
            Inserts an id document into collection "id"
            idMyMongo - MyMongo object for collection "id"
            nowDate - current date
            docId - NLM document id
            Returns True is it a new document False is it was already saved
        """

        doc = {"_id":docId, "status":"aheadofprint"}

        # Check if the new document is already stored in Mongo
        cursor = idMyMongo.search(doc)
        isNew = cursor.count() == 0

        if isNew:  #new document
            doc["firstHarvesting"] = nowDate
        else:
            doc = cursor[0]
        doc["lastHarvesting"] = nowDate

        # Update id onto mongo
        idMyMongo.replaceDoc(doc)

        return isNew


    def __xmlToFile(self,
                    docId,
                    xml,
                    dir=".",
                    encoding="UTF-8",
                    includeXmlHeader=True):
        """
        Writes the xml document into a file
        docId - NLM document id
        xml - string having xml content
        dir - output file directory
        encoding - output file encoding
        """
        header = '<?xml version="1.0" encoding="UTF-8"?>'
        fname = str(docId) + ".xml"

        xdir = dir.strip()
        if not xdir.endswith("/"):
            xdir += "/"

        f = open(xdir+fname, mode="w", encoding=encoding)
        if includeXmlHeader:
            f.write(header + '\n')
        f.write(xml)
        f.close()


    def insertDocs(self,
                   nowDate,
                   idMyMongo,
                   xmlMyMongo,
                   ids,
                   xdir=".",
                   encoding="UTF-8",
                   verbose=False):
        """
        For each id from a list of ids, adds a new id document into mongo id
        collection, add a new document into mongo xml collection and creates a
        new file with xml content.
        nowDate - current date
        idMyMongo - MyMongo object for collection "id"
        xmlMyMongo - MyMongo object for collection "xml"
        ids - a list of NLM document ids
        xdir - output file directory
        encoding - output file encoding
        verbose - if True prints the document is inserted
        """

        newDocs = []
        id_size = len(ids)

        for id_ in ids:
            # Insert id document into collection "id"
            isNewDoc = self.__insertDocId(idMyMongo, nowDate, id_)
            if isNewDoc:
                newDocs.append(id_)
            if (verbose):
                status = "[New]" if isNewDoc else "[Already processed]"
                print("Document id:" + str(id_) + " " + status)

        #input("Press Enter to continue...")


        if len(newDocs) > 0:
            if verbose:
                print("Loading and saving " + str(id_size) + " documents: ",
                                                             end="", flush=True)

            diter = DocIterator(newDocs)

            for dId in diter:
                docId = dId[0]
                xml = dId[1]

                # Save xml content into mongo and file
                docDict = xmltodict.parse(xml)
                doc = {"_id":docId, "date":nowDate, "doc":docDict}
                xmlMyMongo.saveDoc(doc)                      # save into mongo
                self.__xmlToFile(docId, xml, xdir, encoding)    # save into file

            if verbose:
                print()  # to print a new line

    def changeDocStatus(self,
                        nowDate,
                        idMyMongo,
                        xmlMyMongo,
                        xmlDir="."
                        delXmlDoc=True,
                        verbose=False):
        """
        Changes the document status from "aheadofprint" to "published"
        nowDate - current date
        idMyMongo - MyMongo object for collection "id"
        xmlMyMongo - MyMongo object for collection "xml"
        delXmlDoc - if True deletes document from collection "xml"
        verbose - if True prints document id into standard output
        """

        # All documents whose lastHarvesting is lower than nowDate
        query = {"lt":{"lastHarvesting":nowDate}}

        cursor = idMyMongo.search(query)

        for doc in cursor:
            doc.lastHarvesting = nowDate
            doc.status = "published"

            idMyMongo.replaceDoc(doc) # update id mongo doc

            id_ = doc._id

            if delXmlDoc:
                xmlMyMongo.deleteDoc(id_)   # delete xml mongo doc

                xdir = xmlDir.strip()
                if not xdir.endswith("/"):
                    xdir += "/"
                xdir += id_ + ".xml"
                try:
                    os.remove(filename)
                except OSError:
                    pass

            if verbose:
                xstr = " xml deleted." if delXmlDoc else ""
                print("doc[" + id_ + "] status changed." + xstr)
