#!/usr/bin/env python

import datetime
import os

class FileFilterItem(object):
    """
    Contains file properties for filter
    """
    def __init__(self, name=None, mtime=None, size=None):
        self.fileName = name
        self.fileModifyTime = mtime
        self.fileSize = size

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    # def __eq__(self, other):
    #     if type(other) is not type(self):
    #         return False
    #     if self.fileName != other.fileName:
    #         return False
    #     if self.fileModifyTime != other.fileModibyTime:
    #         return False
    #     if self.fileSize != other.fileSize:
    #         return False
    #     return True

    def __ne__(self, other):
        return not self.__eq__(other)

class FileFilterBase(object):
    """
    Base class to filter files from source list to target
    Should get [FileFilterItem] objects
    """
    def __init__(self):
        pass

    def checkItemType(self, fileItem):
        """ Check to match type [FileFilterItem] """
        if not isinstance(fileItem, FileFilterItem):
            raise Exception('invalid type')

    def isMatch(self, fileItem):
        """ Return true, if file is match filter """
        return True

    def filterFiles(self, files):
        """ Return matched files """
        return [f for f in files if self.isMatch(f)]

class FileFilterDays(FileFilterBase):
    """
    Match only files which modification time is newer than matchDays days
    """

    def __init__(self, matchDays=None):
        super(FileFilterDays, self).__init__()
        self.matchDays = 0
        if matchDays:
            self.matchDays = int(matchDays)

    def isMatch(self, fileItem):
        if not self.matchDays:
            return True
        self.checkItemType(fileItem)
        if fileItem.fileModifyTime:
            now = datetime.datetime.now()
            diff = now - fileItem.fileModifyTime
            diffDays = diff.days
            return diffDays < self.matchDays
        return True

class FileFilterMask(FileFilterBase):
    """
    Exclude temporary files by mask (use fnmatch.fnmatch)
    """

    def __init__(self):
        super(FileFilterMask, self).__init__()
        self.excludeMasks = self.defaultMasks()

    def defaultMasks(self):
        result = []
        result.append('.*') # any hidden files
        result.append('~*')  # temp files
        result.append('thumbs.db')  # windows thumbs
        return result

    def addMask(self, fileMask):
        self.excludeMasks.append(fileMask)

    def isMatch(self, fileItem):
        import fnmatch
        self.checkItemType(fileItem)
        for fileMask in self.excludeMasks:
            if fnmatch.fnmatch(fileItem.fileName, fileMask):
                return False
        return True
