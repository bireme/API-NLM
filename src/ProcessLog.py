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

import traceback
from datetime import datetime
from MongoDb import MyMongo
from NLM_AOPFactory import NLM_AOPFactory
from NLM_AOPHarvesting import NLM_AOPHarvesting
# from ProcessLog import ProcessLog


__date__ = 20160509


class ProcessLog:
    def __init__(self,
                 harvesting_,
                 mongodbDoc_,
                 mongodbLog_,
                 owner_,
                 process_):
        """
        Constructor.

        harvesting_ - Harvesting object that makes the document harvesting
        mongodbDoc_ - MongoDb object that contains the 'doc' harvesting
                     collection
        mongodbLog_ - MongoDb object that contains the 'log' log collection
        owner_ - Owner of the process
        process_ - Process name
        """
        self.harvesting = harvesting_
        self.mongodbDoc = mongodbDoc_
        self.mongodbLog = mongodbLog_
        self.owner = owner_
        self.process = process_

    def harvest(self):
        """
        Execute the harvesting and add a document with start time, end time,
        process status and number of collected documents.

        Returns a dictionary with harvesting statistics.
        """
        now = datetime.now()
        dateBegin = datetime.strftime(now, "%Y%m%d")
        hourBegin = datetime.strftime(now, "%H:%M:%S")
        id_ = dateBegin + "-" + hourBegin
        doc = {"_id": id_, "process": self.process + "_harvesting",
               "owner": self.owner, "status": "in process",
               "dataBegin": dateBegin, "hourBegin": hourBegin}
        self.mongodbLog.saveDoc(doc)

        try:
            self.harvesting.harvest(dateBegin, hourBegin)
            status = "finished"
        except (Exception, RuntimeError) as ex:
            traceback.print_stack()
            print("Exception/error generated: " + str(ex))
            status = "broken"

        now2 = datetime.now()
        dateEnd = datetime.strftime(now2, "%Y%m%d")
        hourEnd = datetime.strftime(now2, "%H:%M:%S")
        doc = self.harvesting.getHarvStatDoc(id_,
                                             self.process + "_harvesting",
                                             self.owner, status,
                                             dateBegin, hourBegin,
                                             dateEnd, hourEnd)
        self.mongodbLog.replaceDoc(doc)

        return doc

    def moveDocs(self):
        """
        Move to the working dir the harversted documents.

        Returns a dictionary with harvest moving statistics.
        """
        now = datetime.now()
        dateBegin = datetime.strftime(now, "%Y%m%d")
        hourBegin = datetime.strftime(now, "%H:%M:%S")
        id_ = dateBegin + "-" + hourBegin
        doc = {"_id": id_, "process": self.process + "_moving",
               "owner": self.owner, "status": "in process",
               "dataBegin": dateBegin, "hourBegin": hourBegin}
        self.mongodbLog.saveDoc(doc)

        try:
            self.harvesting.moveDocs(dateBegin, hourBegin)
            status = "finished"
        except (Exception, RuntimeError) as ex:
            traceback.print_stack()
            print("Exception/error generated: " + str(ex))
            status = "broken"

        now2 = datetime.now()
        dateEnd = datetime.strftime(now2, "%Y%m%d")
        hourEnd = datetime.strftime(now2, "%H:%M:%S")
        doc = self.harvesting.getMovStatDoc(id_, self.process + "_moving",
                                            self.owner, status,
                                            dateBegin, hourBegin,
                                            dateEnd, hourEnd)
        self.mongodbLog.replaceDoc(doc)

        return doc

if __name__ == "__main__":
    # Execute only if run as a script

    verbose_ = True

    # mongoHost = "ts01vm.bireme.br"
    mongoHost = "mongodb.bireme.br"
    dbName = "db_AheadOfPrint"
    mid = MyMongo(dbName, "col_Id", mongoHost)
    mdoc = MyMongo(dbName, "col_Doc", mongoHost)
    mlog = MyMongo(dbName, "col_Log", mongoHost)

    process = "aheadofprint"
    owner = "serverofi5"

    factory_ = NLM_AOPFactory()
    factory_.setMyMongoId(mid)
    factory_.setMyMongoDoc(mdoc)
    factory_.setXmlOutDir("../xml")
    factory_.setXmlProcDir("../wrk")
    factory_.setProcess(process)
    factory_.setOwner(owner)
    harvesting = NLM_AOPHarvesting(factory_, verbose_)

    log = ProcessLog(harvesting, mdoc, mlog, owner, process)
    result = log.harvest()

    if verbose_:
        print("Process=" + process)
        print("Owner=" + result["owner"])
        print("Status=" + result["status"])
        print("DateBegin=" + result["dateBegin"])
        print("HourBegin=" + result["hourBegin"])
        print("DateEnd=" + result["dateEnd"])
        print("HourEnd=" + result["hourEnd"])
        print("TotAheadDocs=" + str(result["totAheadDocs"]))
        print("TotNoAheadDocs=" + str(result["totNoAheadDocs"]))
        print("NewAheadDocs=" + str(result["newAheadDocs"]))
        print("NewNoAheadDocs=" + str(result["newNoAheadDocs"]))

    result = log.moveDocs()

    if verbose_:
        print("Process=" + process)
        print("Owner=" + result["owner"])
        print("Status=" + result["status"])
        print("DateBegin=" + result["dateBegin"])
        print("HourBegin=" + result["hourBegin"])
        print("DateEnd=" + result["dateEnd"])
        print("HourEnd=" + result["hourEnd"])
        print("TotMovedDocs=" + str(result["totMovedDocs"]))
