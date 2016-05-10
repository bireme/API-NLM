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

from os import listdir, makedirs, remove
from os.path import isdir, exists, join
import fnmatch
import shutil

__date__ = 20160418


def xmlToFile(docId,
              xml,
              toDir=".",
              encoding="UTF-8",
              includeXmlHeader=True,
              createDir=True):
    """
    Write the xml document into a file.

    docId - NLM document id
    xml - string having xml content
    toDir - output file directory
    encoding - output file encoding
    includeXmlHeader - it True includes the header '<?xml ...' into file
    createDir - True if the destination directory should be created if it does
                  not exists
    """
    if not exists(toDir):
        if createDir:
            makedirs(toDir)
        else:
            raise Exception("toDir does not exists")

    header = '<?xml version="1.0" encoding="UTF-8"?>'
    fname = str(docId) + ".xml"

    f = open(join(toDir, fname), mode="w", encoding=encoding)
    if includeXmlHeader:
        f.write(header + '\n')
    f.write(xml)
    f.close()


def moveFiles(fromDir,
              toDir,
              fileFilter="*",
              createToDir=True,
              moveSubDirs=False):
    """
    Move files from a directory to another one.

    fromDir - origin directory path
    toDir - destination directory path
    fileFilter - filter to choose which files will be moved
    createToDir - True if the destination directory should be created if
                  it does not exists
    moveSubDirs - True if besides standard files, subdirectories also should
                  be moved
    """
    if not isdir(fromDir):
        raise Exception("fromDir does not exists")

    if not exists(toDir):
        if createToDir:
            makedirs(toDir)
        else:
            raise Exception("toDir does not exists")

    for f in listdir(fromDir):
        if fnmatch.fnmatch(f, fileFilter):
            from_ = join(fromDir, f)
            to = join(toDir, f)
            if isdir(from_):
                # print("diretorio:" + f)
                if moveSubDirs:
                    shutil.move(from_, to)
            else:
                shutil.move(from_, to)


def copyFiles(fromDir,
              toDir,
              fileFilter="*",
              createToDir=True,
              copySubDirs=False):
    """
    Copy files from a directory to another one.

    fromDir - origin directory path
    toDir - destination directory path
    fileFilter - filter to choose which files will be copied
    createToDir - True if the destination directory should be created if it
                  does not exists
    copySubDirs - True if besides standard files, subdirectories also should
                  be copied
    """
    if not isdir(fromDir):
        raise Exception("fromDir does not exists")

    if not exists(toDir):
        if createToDir:
            makedirs(toDir)
        else:
            raise Exception("toDir does not exists")

    for f in listdir(fromDir):
        if fnmatch.fnmatch(f, fileFilter):
            from_ = join(fromDir, f)
            to = join(toDir, f)
            if isdir(from_):
                print("diretorio:" + f)
                if copySubDirs:
                    shutil.copy2(from_, to)
            else:
                shutil.copy2(from_, to)


def readFile(filePath,
             encoding="UTF-8"):
    """

    filePath - the path (dir+name) of the file
    encoding - character encoding of the file
    Returns a string with the file content
    """
    f = open(filePath, encoding=encoding)
    str_ = f.read()
    f.close()

    return str_


def removeFile(filePath):
    """
    Delete a file.

    filePath - the path (dir+name) of the file
    """
    remove(filePath)


def existFile(filePath):
    """
    Check if a file exists.

    filePath - the path (dir+name) of the file
    Returns True if a file exists
    """
    return exists(filePath)
