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
                  retmax=100,
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
            print("count=" + str(count))
            if (useHistory):
                web = xml.getXPath("eSearchResult/WebEnv")[0][0]
                key = xml.getXPath("eSearchResult/QueryKey")[0][0]

            if (retmax > 0):
                id_list = xml.getXPath("eSearchResult/IdList/Id")
                for id in id_list:
                    ids.append(id[0])

        return (count, web, key, ids)
