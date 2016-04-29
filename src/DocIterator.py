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

class DocIterator:
    def __init__(self,
                 ids,
                 dbName="pubmed",
                 retType="MEDLINE",
                 retMode="XML",
                 xpathSplit="PubmedArticleSet/PubmedArticle",
                 verbose=True):
        """
            ids - list of xml document ids to be downloaded
            dbName - database  name
            retType - see efetch 'rettype' documentation
            retMode - see efetch 'retmode' documentation
            xpathSplit - the xpath expression used to extract the desired xml
                         documents from the big one downloaded with efetch
            verbose - if True print a dot in the standard output when a block is loaded
        """
        base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        size = 50 #100

        self.ids = ids
        self.total = len(ids)
        if self.total == 0:
            raise Exception("Empty id list")

        self.blockSize =  size if self.total > size else self.total
        self.lastBlock = (self.total / self.blockSize) - 1
        self.curBlock = 0
        self.curBlkPos = 0
        self.xmlBlock = []
        self.xpath = xpathSplit
        self.url = base
        self.postParam = {"db":dbName, "retmax":str(self.blockSize),
                          "rettype":retType, "retmode":retMode}
        self.verbose = verbose
        self.__loadBlock(0)


    def __iter__(self):
        """
        Turns this class iterable
        """
        return self


    def __next__(self):
        """
        Returns the next pair (<id>,<downloaded xml document>)
        """
        #print("entra no next")
        xml = None
        if self.curBlkPos <= len(self.xmlBlock) - 1:
            xml = self.xmlBlock[self.curBlkPos]
            self.curBlkPos += 1
        else:
            if self.curBlock < self.lastBlock:
                self.__loadBlock(self.curBlock + 1)
                xml = self.__next__()
            else:
                #print("StopIteration")
                raise StopIteration()
        #print("sai do next")
        return xml


    def __loadBlock(self,
                    blkNumber):
        """
        Loads the document buffer with the next documents.
        blkNumber - the block number to be downloaded (initial block is 0)
        """

        if self.verbose:
            print('.', end="", flush=True)

        block = []
        retStart = blkNumber * self.blockSize
        if retStart < self.total:
            pair = self.__getIds(retStart)
            self.postParam["id"] = pair[1]
            xmlRes = loadUrl(self.url, post_values=self.postParam)
            del self.postParam["id"]
            if xmlRes[0] == 200:
                #print("res=" + str(xmlRes[1]))
                block = self.__splitBlock(pair[0], xmlRes[1])
                self.curBlock = blkNumber
                self.curBlkPos = 0
            else:
                raise Exception("ErrCode:" + str(xmlRes[0]) + " reason:" /
                                  + xmlRes[1] + " url:" + self.url)
        else:
            raise StopIteration()

        self.xmlBlock = block
        #print("tamanho do bloco: " + str(len(self.xmlBlock)))

    def __splitBlock(self,
                     ids,
                     xml):
        """
        Extracts from the downloaded content the desired documents using the
        xpathSplit xpath expression

        ids = list of document ids
        xml - the downloaded xml to be splited
        Returns a list of pairs (<id>, <xml document>)
        """
        ret = []
        idx = 0
        mxml = MyXML(xml)
        elems = mxml.getXPathElements(self.xpath)
        for elem in elems:
            ret.append((ids[idx], mxml.getTreeString(elem).strip()))
            idx += 1
        #s = str(len(ret))
        #print("size=" + s)
        return ret


    def __getIds(self,
                 retStart):
        """
        Retrieves the next ids to be used to download the xml documents
        retStart - the initial id position
        Returns a pair (<list of ids>, <string with next ids>)
        """
        ids_ = []
        strg = ""
        last = min(retStart + self.blockSize, self.total)
        first = True

        for idx in range(retStart,last):
            if first:
                first = False
            else:
                strg += ","
            id = self.ids[idx]
            ids_.append(id)
            strg += str(id)

        return (ids_,strg)
