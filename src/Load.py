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

from MongoDb import MyMongo
from NLM_AOPFactory import NLM_AOPFactory
from NLM_AOPHarvesting import NLM_AOPHarvesting
from ProcessLog import ProcessLog

__date__ = 20160701

if __name__ == "__main__":
    # Execute only if run as a script.

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
    factory_.setXmlProcDir("/bases/mdlG4/fasea/aheadofprint")
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
        print("TotInProcessDocs=" + str(result["totInProcessDocs"]))
        print("TotMovedDocs=" + str(result["totMovedDocs"]))
        print("NewAheadDocs=" + str(result["newAheadDocs"]))
        print("NewInProcessDocs=" + str(result["newInProcessDocs"]))
        print("NewNoAheadDocs=" + str(result["newNoAheadDocs"]))
        print("")
