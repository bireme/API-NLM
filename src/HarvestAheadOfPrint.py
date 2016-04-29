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

from MongoDb import MyMongo as db_connection
from LoadUrl import loadUrl 
from NLM_API import NLM_API
from DocIterator import DocIterator
import os
import datetime

class HarvestAheadOfPrint:
    def __init__(self, database, collection_id, collection_xml, host="localhost", port=27017):
        """
        database - the mongo database name
        collection_id - the id collection name
        collection_xml - the xml collection name
        host - url of the mongo server host
        port - mongo server port
        """
        self.db = database
        self.col_id = collection_id
        self.col_xml = collection_xml
        self.host = host
        self.port = port


    def harvestInsert(self):

        # conexao com o banco para colecao de id
        job_id = db_connection(self.db, self.col_id, self.host)

        # conexao com o banco para colecao de xml
        job_xml = db_connection(self.db, self.col_xml, self.host)

        # Apaga temporariamente as coleções
        job_id.dropCollection()
        job_xml.dropCollection()

        harvest = NLM_API()
        id_count = harvest.getDocIds(retmax=0)

        id_total = int(id_count[0])
        #### TEMPORARIO PARA TESTE
        id_total = 35

        print ('total :', id_total)

        count = 0
        while (count <= id_total ):
            print ('+ ', count,'################################################################################')

            id_list = harvest.getDocIds(retmax=10,retstart=count)

            # obtendo id e o xml
            xml_list =  DocIterator(id_list[3])
 
            for xml in xml_list:
                # print(xml)
                print("-------------------------------------------------------------------")

                # grava xml na colecao col_xml
                job_xml.saveDoc({"last_modified": datetime.datetime.now(),'xml_content':xml})

            count = count + 10

h = HarvestAheadOfPrint("db_pubmed_aheadofprint", "cold_id", "col_xml")
do = h.harvestInsert()

