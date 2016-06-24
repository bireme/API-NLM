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
from Harvesting import Harvesting
from MongoDb import MyMongo
from NLM_AheadOfPrint import NLM_AheadOfPrint
from NLM_AOPFactory import NLM_AOPFactory

__date__ = 20160418


class NLM_AOPHarvesting(Harvesting):
    def __init__(self,
                 factory,
                 verbose):
        """
        Constructor.

        factory - a NLM_AOPFactory object
        verbose - if True debug messages are printed at scream
        """
        super().__init__(factory.myMongoId, factory.myMongoDoc)
        self.ahead = NLM_AheadOfPrint(factory)
        self.verbose = verbose

    def harvest(self,
                dateBegin,
                hourBegin):
        """
        Do the harvesting of the documents.

        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        """
        if self.verbose:
            print("----------------------------------------------------------")
            print("Step 1 - Downloads and saves NLM Pubmed ahead of print " +
                  "documents")
            print("----------------------------------------------------------")

        self.ahead.process(dateBegin, hourBegin, self.verbose)

    def moveDocs(self,
                 dateBegin,
                 hourBegin):
        """
        Move to the working dir the harversted documents.

        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        """
        if self.verbose:
            print("----------------------------------------------------------")
            print("Step 2 - Copy unique docs to the standard Medline " +
                  "download dir")
            print("----------------------------------------------------------")

        self.ahead.syncWorkDir(dateBegin, hourBegin, self.verbose)

    def getHarvStatDoc(self,
                       id_,
                       process,
                       owner,
                       status,
                       dateBegin,
                       hourBegin,
                       dateEnd,
                       hourEnd):
        """
        Return a dictionary with harvesting statistic info.

        id_ - document id
        process - process name
        owner - process owner
        status - process result status
        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        dateEnd - process end date YYYYMMDD
        hourEnd - process end time HH:MM:SS
        """
        query0 = {"status": "no_aheadofprint"}
        query1 = {"date": dateBegin, "hour": hourBegin,
                  "status": "aheadofprint"}
        query2 = {"date": dateBegin, "hour": hourBegin,
                  "status": "in process"}
        query3 = {"date": dateBegin, "hour": hourBegin,
                  "status": "no_aheadofprint"}
        totalAheadDocs = self.mdoc.search({}).count()
        totalNoAheadDocs = self.mid.search(query0).count()
        newAheadDocs = self.mid.search(query1).count()
        newInProcessDocs = self.mid.search(query2).count()
        newNoAheadDocs = self.mid.search(query3).count()

        doc = {"_id": id_,
               "process": process, "owner": owner, "status": status,
               "totAheadDocs": totalAheadDocs,
               "totNoAheadDocs": totalNoAheadDocs,
               "newAheadDocs": newAheadDocs,
               "newInProcessDocs": newInProcessDocs,
               "newNoAheadDocs": newNoAheadDocs,
               "dateBegin": dateBegin, "hourBegin": hourBegin,
               "dateEnd": dateEnd, "hourEnd": hourEnd}

        return doc

    def getMovStatDoc(self,
                      id_,
                      process,
                      owner,
                      status,
                      dateBegin,
                      hourBegin,
                      dateEnd,
                      hourEnd):
        """
        Return a dictionary with moving statistic info.

        id_ - document id
        process - moving process name
        owner - moving process owner
        status - moving process status result
        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        dateEnd - process end date YYYYMMDD
        hourEnd - process end time HH:MM:SS
        """
        query = {"date": dateBegin, "hour": hourBegin,
                 "status": "moved"}
        totalMovedDocs = self.mid.search(query).count()

        doc = {"_id": id_,
               "process": process, "owner": owner, "status": status,
               "totMovedDocs": totalMovedDocs,
               "dateBegin": dateBegin, "hourBegin": hourBegin,
               "dateEnd": dateEnd, "hourEnd": hourEnd}

        return doc

if __name__ == "__main__":
    # execute only if run as a script

    verbose_ = True
    mongoHost = "ts01vm.bireme.br"
    dbName = "db_AheadOfPrint"
    idColName = "col_Id"
    docColName = "col_Doc"
    mid = MyMongo(dbName, idColName, mongoHost)
    mdoc = MyMongo(dbName, docColName, mongoHost)

    factory_ = NLM_AOPFactory()
    factory_.setMyMongoId(mid)
    factory_.setMyMongoDoc(mdoc)
    factory_.setXmlOutDir("../xml")
    factory_.setXmlProcDir("")

    harvesting = NLM_AOPHarvesting(factory_, verbose_)

    now1 = datetime.now()
    date1 = datetime.strftime(now1, "%Y-%m-%d")
    hour1 = datetime.strftime(now1, "%H:%M:%S")
    harvesting.harvest(date1, hour1)

    now2 = datetime.now()
    date2 = datetime.strftime(now2, "%Y-%m-%d")
    hour2 = datetime.strftime(now2, "%H:%M:%S")
    harvesting.moveDocs(date2, hour2)
