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


class LogDocument:
    def __init__(self,
                 date,
                 hour,
                 process,
                 owner):
        """
        date - current date with format: YYYY-MM-DD
        hour - current time with format: HH:MM:SS
        process - harvesting process name
        owner - owner of the process
        """
        self.date = date
        self.hour = hour
        self.process = process
        self.owner = owner

    def getNewDoc(self,
                  id_,
                  status):
        """

        id_ - document id
        status - document status: aheadofprint or no_aheadofprint
        Returns a new document
        """
        doc = {"id": id_}
        doc["date"] = self.date
        doc["hour"] = self.hour
        doc["process"] = self.process
        doc["status"] = status
        doc["owner"] = self.owner

        return doc
