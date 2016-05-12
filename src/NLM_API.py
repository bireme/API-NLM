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

import time
from LoadUrl import loadUrl
from XML import MyXML

__date__ = 20160418


class NLM_API:
    def __init__(self):
        self.eutils = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def listDatabases(self):
        """
        List the databases that can be used by eutils api.

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
        List the fields of a database.

        dbname - the database name
        Returns a list of field names
        """
        info = []
        xmlRes = loadUrl(self.eutils + "/einfo.fcgi?db=" + dbname +
                         "&version=2.0")

        if xmlRes[0] == 200:
            xml = MyXML(xmlRes[1])
            info = xml.getXPathChildText("eInfoResult/DbInfo/FieldList/Field",
                                         ['Name', 'FullName', 'Description'])

        return info

    def getAllIds(self,
                  dbname="pubmed",
                  query="pubstatusaheadofprint",
                  verbose=True):
        """

        dbname - database name
        query - expression used to retrieve the document ids
        Returns a pair as follows:
            (<<#ofIds>, <list with all ids retrieved from a search>)
        """
        idTuple = self.getDocIds(dbname, query, retmax=0, verbose=verbose)
        numOfDocs = int(idTuple[0])

        idList = []
        max_ = 1000
        startPos = 0

        while startPos < numOfDocs:
            if verbose:
                print(".", end='', flush=True)
            idTuple = self.getDocIds(dbname, query, retmax=max_,
                                     retstart=startPos, verbose=verbose)
            idList.extend(idTuple[3])
            startPos += max_

        if verbose:
            print()

        return numOfDocs, idList

    def getDocIds(self,
                  dbname="pubmed",
                  query="pubstatusaheadofprint",
                  retmax=1000,
                  retstart=0,
                  field=None,
                  useHistory=False,
                  waitSeconds=30,
                  verbose=True):
        """

        dbname - database name
        query - expression used to retrieve the document ids
        retmax - the maximum number of returned ids
        retstart - initial position (from id list) used to return ids
        field - if used narrow the search to that field
        useHistory - true if the retrieved ids should the stored in the server
                     for temporary and future use by efetch.
        waitSeconds - number of seconds the program will sleep it download
                      fails
        verbose - True if some info should be printed into screen
        Returns a tuple as follows:
               (<#ofIds>, <webenv>, <querykey>, <list of the document ids that
               are retrieved by a query>)
        """
        if retmax > 100000:
            raise Exception("retamax > 100.000")

        url = self.eutils + "/esearch.fcgi?db=" + dbname + "&term=" + \
              query + "&retstart=" + str(retstart)

        if useHistory:
            url += "&usehistory=y"
            retmax = 0
        if field is not None:
            url += "&field=" + field

        url += "&retmax=" + str(retmax)

        count = 0
        web = ""
        key = ""
        ids = []

        xmlRes = loadUrl(url)
        if xmlRes[0] == 200:
            xml = MyXML(xmlRes[1])
            count = xml.getXPath("eSearchResult/Count")[0][0]
            # print("count=" + str(count))
            if useHistory:
                web = xml.getXPath("eSearchResult/WebEnv")[0][0]
                key = xml.getXPath("eSearchResult/QueryKey")[0][0]

            if retmax > 0:
                id_list = xml.getXPath("eSearchResult/IdList/Id")
                for id_ in id_list:
                    ids.append(id_[0])
        else:
            if waitSeconds <= 3600:  # waits up to 1 hour and try again
                if verbose:
                    print("(" + str(waitSeconds) + "s)", end="",
                          flush=True)
                time.sleep(waitSeconds)
                self.getDocIds(dbname, query, retmax, retstart, field,
                               useHistory, waitSeconds * 2, verbose)
            else:
                raise Exception("ErrCode:" + str(xmlRes[0]) + " reason:" +
                                xmlRes[1] + " url:" + self.url)

        return count, web, key, ids
