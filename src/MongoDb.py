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

import pymongo
from pymongo import MongoClient

__date__ = 20160418

class MyMongo:
    def __init__(self,
                 database,
                 collection,
                 host="localhost", 
                 port=27017):
        """
        database - the mongo database name
        collection - the collection name
        host - url of the mongo server host
        port - mongo server port
        """
        self.client = MongoClient(host, port)
        self.db = self.client[database]
        self.col = self.db[collection]

    def saveDoc(self, doc):
        """
        Saves a new document into the selected collection
        doc - mongo document represented as a dictionary
        """
        self.col.insert_one(doc)

    def replaceDoc(self, doc):
        """
        Replaces an exiting saved document by a new one with the same _id field
        doc - mongo document represented as a dictionary
        """
        _id = {'_id' : doc['_id']}
        self.col.replace_one(_id, doc, upsert=True)

    def loadDoc(self, id):
        """
        id - mongo document _id field
        Returns a saved document
        """
        return self.col.find_one(id)

    def loadDocs(self, query = {}):
        """
        query - mongo document pattern represented as a dictionary to be used
                as a filter
        Returns an ordered pair of type (<size of the list>,<list of documents>)
        """
        cursor = self.col.find(query)
        return (cursor.count(), cursor)

    def deleteDoc(self, id):
        """
        Deletes a document from the collection
        id - mongo document _id field
        Returns True if the deletion was ok or False if not
        """
        idd = {'_id' : id}
        return (self.col.delete_one(idd).deleted_count == 1)

    def numOfDocs(self):
        """
        Returns the number of documents of this collection
        """
        return self.col.count()

    def createIndex(self, name, fieldNames):
        """
        Creates an index for this collection
        name - the index name
        fieldNames - list of mongo document fields to be indexed
        """

        flds = []
        for fname in fieldNames:
            flds.append((fname, pymongo.ASCENDING))
        self.col.create_index(flds, name=name)

    def dropIndex(self, name):
        """
        Deletes an index
        name - the index name
        """
        self.col.drop_index(name)

    def reindexAll(self):
        """
        Reindex all indexes
        """
        self.col.reindex()

    def listIndexes(self):
        """
        Returns a list of names of the collection indexes
        """
        idx = []
        for index in self.col.list_indexes():
            idx.append(index['name'])
        return idx

    def dropCollection(self):
        """
        Deletes the collection from the database
        """

        self.db.drop_collection(self.col)

    def search(self,
               query=None,
               retFldNames=None):
        """
        Searches documents
        query - map with field/value elements
        retFldName - list of field names returned into retrieved documents
        Returns an iterable of documents
        """
        return self.col.find(query, retFldNames)
