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

__date__ = 20160509


class Harvesting(object):
    def __init__(self,
                 mongodbId,
                 mongodbDoc):
        """
        Constructor.

        mongodbDoc - MongoDb object that contains the 'doc' harvesting
                     collection
        mongodbLog - MongoDb object that contains the 'log' log collection
        """
        self.mid = mongodbId
        self.mdoc = mongodbDoc

    def harvest(self,
                dateBegin,
                hourBegin):
        """
        Execute the harverst.

        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        """
        pass

    def moveDocs(self,
                 dateBegin,
                 hourBegin):
        """
        Move to the working dir the harversted documents.

        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        """
        pass

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
        doc = {"_id": id_, "process": process,
               "owner": owner, "status": status,
               "dateBegin": dateBegin, "hourBegin": hourBegin,
               "dateEnd": dateEnd, "hourEnd": hourEnd}

        return doc

    def getMovStatDoc(self,
                      id_,
                      process,
                      owner,
                      status,
                      totalMovedDocs,
                      dateBegin,
                      hourBegin,
                      dateEnd,
                      hourEnd):
        """
        Return a dictionary with moving statistic info.

        id_ - document id
        process - process name
        owner - process owner
        status - process result status
        totalMovedDocs - number of moved docs from harvesting to working
                         directory
        dateBegin - process begin date YYYYMMDD
        hourBegin - process begin time HH:MM:SS
        dateEnd - process end date YYYYMMDD
        hourEnd - process end time HH:MM:SS
        """
        doc = {"_id": id_, "process": process,
               "owner": owner, "status": status,
               "totalMovedDocs": totalMovedDocs,
               "dateBegin": dateBegin, "hourBegin": hourBegin,
               "dateEnd": dateEnd, "hourEnd": hourEnd}

        return doc
