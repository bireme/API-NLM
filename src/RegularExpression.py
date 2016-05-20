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

import re

__date__ = 20160520


class RegularExpression:
    def __init__(self,
                 regexp,
                 dotAll=False,
                 ignoreCase=False,
                 multiline=False):
        """
        Constructor.

        regexp - regular expression to be used
        dotAll - make . match any character, including newlines
        ignoreCase - do case-insensitive matches
        multilne - multi-line matching, affecting ^ and $
        """
        flags = 0
        if dotAll:
            flags |= re.DOTALL
        if ignoreCase:
            flags |= re.IGNORECASE
        if multiline:
            flags |= re.MULTILINE
        self.reg = re.compile(regexp, flags)

    def findAll(self,
                str_):
        """
        Find all occurrences of matches in the str_.

        str = string where the regular expression will be search
        Return a list of strings
        """
        return self.reg.findall(str_)
