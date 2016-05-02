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

from NLM_AheadOfPrint import NLM_AheadOfPrint

ahead = NLM_AheadOfPrint("ts01vm.bireme.br",
                         "db_AheadOfPrint",
                         "col_Id",
                         "col_Xml",
                         "../xml")

print("-----------------------------------------------------------------------")
print("Step 1 - Downloads and saves NLM Pubmed ahead of print documentes")
print("-----------------------------------------------------------------------")

ahead.process()

print("\n-----------------------------------------------------------------------")
print("Step 2 - Move unique documents to the standard Medline download directory")
print("-----------------------------------------------------------------------")

#ahead.syncWorkDir(workDir)
