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

    def harvest(self):
        """Execute the harverst."""
        pass

    def getStatDoc(self,
                   id_,
                   process,
                   owner,
                   status,
                   dateBegin,
                   hourBegin,
                   dateEnd,
                   hourEnd):
        """
        Return a dictionary with statistic info.

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
