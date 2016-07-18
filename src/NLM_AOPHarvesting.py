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
            print("Downloads and saves NLM Pubmed ahead of print documents")
            print("----------------------------------------------------------")

        self.ahead.process(dateBegin, hourBegin, self.verbose)

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
        query0 = {"status": "aheadofprint"}
        query1 = {"status": "no_aheadofprint"}
        query2 = {"status": "in process"}
        query3 = {"date": dateBegin, "hour": hourBegin,
                  "status": "aheadofprint"}
        query4 = {"date": dateBegin, "hour": hourBegin,
                  "status": "in process"}
        query5 = {"date": dateBegin, "hour": hourBegin,
                  "status": "no_aheadofprint"}
        totalAheadDocs = self.mid.search(query0).count()
        totalNoAheadDocs = self.mid.search(query1).count()
        totalInProcessDocs = self.mid.search(query2).count()
        newAheadDocs = self.mid.search(query3).count()
        newInProcessDocs = self.mid.search(query4).count()
        newNoAheadDocs = self.mid.search(query5).count()

        doc = {"_id": id_,
               "process": process, "owner": owner, "status": status,
               "totAheadDocs": totalAheadDocs,
               "totNoAheadDocs": totalNoAheadDocs,
               "totInProcessDocs": totalInProcessDocs,
               "newAheadDocs": newAheadDocs,
               "newInProcessDocs": newInProcessDocs,
               "newNoAheadDocs": newNoAheadDocs,
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

    harvesting = NLM_AOPHarvesting(factory_, verbose_)

    now = datetime.now()
    date = datetime.strftime(now, "%Y-%m-%d")
    hour = datetime.strftime(now, "%H:%M:%S")
    harvesting.harvest(date, hour)
