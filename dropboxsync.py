#!/usr/bin/env python

import logging
import contextlib

import datetime
import dropbox
from dropbox.files import FileMetadata, FolderMetadata
import os
import time
import filters
import unicodedata

class DropboxSync(object):
    """
    Class to help synchronize files to/from dropbox
    use Dropbox API v2 (https://github.com/dropbox/dropbox-sdk-python)
    """
    def __init__(self, args):
        self.args=args
        self.dbx = None
        self.localDir = self.normalizeDir(args['localdir'])
        self.dropboxDir = self.normalizeDir(args['dropboxdir'])
        self.directionToDb = args['direction'] == 'todropbox'

        self.timeoutSec = 2 * 60
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.dbList = []
        self.locList = []
        self.filterItems = []
        self.sourceFilesMatched = []

    def setLogger(self, logger):
        self.logger = logger

    # prepare
    def prepare(self):
        self.logger.info('--- Mode: %s' % self.args['direction'])
        self.prepareDropboxAuth()
        self.checkDropboxAuth()
        self.checkDropboxDir()
        self.checkLocalDir()

        self.listDropboxFiles()
        self.listLocalFiles()
        self.listFilterItems()

    def prepareDropboxAuth(self):
        self.logger.debug('Connecting to dropbox using token...')
        self.dbx = dropbox.Dropbox(self.args['token'])
        self.logger.debug('Dropbox connected')

    def checkLocalDir(self):
        if not os.path.exists(self.localDir):
            raise Exception('Local path is not exists:%s' % self.localDir)
        if not os.path.isdir(self.localDir):
            raise Exception('Local path is not directory:%s' % self.localDir)

    def checkDropboxAuth(self):
        """
        Checks Dropbox uploader is initialized to Dropbox account
        """
        self.logger.debug('Getting info about dropbox account...')
        acc = self.dbx.users_get_current_account()
        self.logger.debug('Dropbox account: [%s_%s] mail:%s' % (acc.country, acc.locale, acc.email))

    def checkDropboxDir(self):
        """
        Checks that Dropbox folder exists.
        """
        self.logger.debug('Checking if Dropbox folder exists...')
        try:
            self.dbx.files_list_folder(self.dropboxDir)
            self.logger.debug('Dropbox folder exists')
        except:
            self.logger.error(f"Folder {self.dropboxDir} does not exist on Dropbox")
            exit(-1)


    def listLocalFiles(self):
        self.logger.debug('Getting list of local files...')
        locList = [unicodedata.normalize('NFC', f.decode('utf-8')) for f in os.listdir(self.localDir) if os.path.isfile(os.path.join(self.localDir,f))]
        self.locList = [self.filterItemByLocal(f) for f in locList]
        self.logger.debug('Local files:%s' % len(self.locList))
        return True

    def mtime(self, filePath):
        mtime = os.path.getmtime(filePath)
        return datetime.datetime(*time.gmtime(mtime)[:6])
        # t = os.path.getmtime(filePath)
        # return datetime.datetime.fromtimestamp(t)

    def filterItemByLocal(self, fileName):
        filePath = os.path.join(self.localDir, fileName)
        return filters.FileFilterItem(
            name=fileName,
            mtime=self.mtime(filePath),
            size=os.path.getsize(filePath))

    def filterItemByDropbox(self, fileMd):
        return filters.FileFilterItem(
            name=fileMd.name,
            mtime=fileMd.client_modified,
            size=fileMd.size
        )

    def normalizeDir(self, directory):
        result = directory.replace(os.path.sep, '/')
        result = os.path.expanduser(result)
        while '//' in result:
            result = result.replace('//', '/')
        result = result.rstrip('/')
        result = unicodedata.normalize('NFC', result)
        return result

    # filtration
    def listFilterItems(self):
        resItems = []
        if self.directionToDb:
            self.filterItems = self.locList
        else:
            self.filterItems = self.dbList

    def filterSourceFiles(self, filters):
        resFiles = self.filterItems
        sourceCount = len(resFiles)
        self.logger.debug('Source files:%s' % (len(resFiles)))
        for fltr in filters:
            prevCount = len(resFiles)
            resFiles = fltr.filterFiles(resFiles)
            resCount = len(resFiles)
            if resCount != prevCount:
                self.logger.debug('Filter \'%s\': %s -> %s' % (fltr.__class__.__name__, prevCount, resCount))
        self.sourceFilesMatched = resFiles
        self.logger.info('--- Filter source files: %d -> %d' % (sourceCount, len(resFiles)))

    # synchronize
    def synchronize(self):
        # for debug
        #self.fixLocalTimestamps()

        if self.directionToDb:
            self.deleteDropboxFiles()
            self.syncToDropbox()
        else:
            self.deleteLocalFiles()
            self.syncToLocal()

        return True

    def deleteLocalFiles(self):
        # remove local
        sourceNames = [fileItem.fileName for fileItem in self.sourceFilesMatched]
        delList = [fileItem for fileItem in self.locList if fileItem.fileName not in sourceNames]
        if not delList:
            return
        self.logger.debug('Local files to delete:%s' % len(delList))
        for fileItem in delList:
            os.remove(os.path.join(self.localDir, fileItem.fileName))
        self.logger.info('--- Delete %d/%d local files' % (len(delList), len(self.locList)))

    def syncToLocal(self):
        countSuccess = 0
        countSkip = 0
        countFails = 0
        for fileItem in self.sourceFilesMatched:
            if fileItem in self.locList:
                self.logger.debug('Skip existed:%s' % fileItem.fileName)
                countSkip += 1
                continue
            if self.downloadFile(fileItem):
                countSuccess += 1
            else:
                countFails += 1
        # print stat
        strSkip = ' Skip:%d' % countSkip if countSkip else ''
        strFails = ' Fails:%d' % countFails if countFails else ''
        self.logger.info('--- Download %d/%d%s%s' % (countSuccess, len(self.sourceFilesMatched), strSkip, strFails))

    def deleteDropboxFiles(self):
        """ Delete not matched files from Dropbox directory """
        sourceNames = [fileItem.fileName for fileItem in self.sourceFilesMatched]
        delList = [fileItem for fileItem in self.dbList if fileItem.fileName not in sourceNames]
        if not delList:
            return
        self.logger.debug('Dropbox files to delete:%s' % len(delList))
        for fileItem in delList:
            self.deleteFile(fileItem)
        self.logger.info('--- Success delete %d/%d dropbox files' % (len(delList), len(self.dbList)))

    def syncToDropbox(self):
        countSuccess = 0
        countSkip = 0
        countFails = 0
        for fileItem in self.sourceFilesMatched:
            if fileItem in self.dbList:
                self.logger.debug('Skip existed:%s' % fileItem.fileName)
                countSkip += 1
                continue
            if self.uploadFile(fileItem):
                countSuccess += 1
            else:
                countFails += 1
        # print stat
        strSkip = ' Skip:%d' % countSkip if countSkip else ''
        strFails = ' Fails:%d' % countFails if countFails else ''
        self.logger.info('--- Success upload %d/%d%s%s' % (countSuccess, len(self.sourceFilesMatched), strSkip, strFails))

    # dropbox helpers
    def listDropboxFiles(self):
        """List a folder.
        Return an array of filter items
        """
        path = self.dropboxDir
        self.logger.debug('Downloading dropbox list files...')

        try:
            with self.stopwatch(__name__):
                res = self.dbx.files_list_folder(path)
        except dropbox.exceptions.ApiError as err:
            self.dbList = []
            raise Exception('Folder listing failed for %s -- assumed empty:%s' % (path, err))
        else:
            self.logger.debug('Dropbox files:%s' % len(res.entries))
            self.dbList = [self.filterItemByDropbox(fileMd) for fileMd in res.entries]

    def downloadFile(self, fileItem):
        """Download a file.
        Return True when success, or False if error occurs.
        """
        fileName = fileItem.fileName
        dbItem = next((f for f in self.dbList if f.fileName == fileName), None)
        dbPath = os.path.join(self.dropboxDir, fileName)
        locPath = os.path.join(self.localDir, fileName)
        self.logger.debug('Downloading %s (%d bytes) ...' % (fileName, dbItem.fileSize))
        with self.stopwatch('downloading'):
            try:
                md = self.dbx.files_download_to_file(locPath, dbPath)
            except dropbox.exceptions.ApiError as err:
                raise Exception('%s - API error:%s' % (fileName, err))
        self.logger.debug('Success download - %s (%d bytes)' % (fileName, dbItem.fileSize))
        return True

    def uploadFile(self, fileItem):
        """Upload a file.
        Return the request response, or None in case of error.
        """
        fileName = fileItem.fileName
        dbPath = os.path.join(self.dropboxDir, fileName)
        locPath = os.path.join(self.localDir, fileName)
        mode = dropbox.files.WriteMode.overwrite
        # mtime0 = os.path.getmtime(locPath)
        # mtime = datetime.datetime(*time.gmtime(mtime0)[:6])
        mtime = self.mtime(locPath)
        with open(locPath, 'rb') as f:
            data = f.read()
        self.logger.debug('Uploading %s (%d bytes) ...' % (fileName, len(data)))
        # self.logger.debug('mtime %d %d ...' % (mtime, fileItem.fileModifyTime))
        with self.stopwatch('uploading'):
            try:
                res = self.dbx.files_upload(
                    data, dbPath, mode,
                    client_modified=mtime,
                    autorename=False,
                    mute=True)
            except dropbox.exceptions.ApiError as err:
                raise Exception('%s - API error:%s' % (fileName, err))
        # self.logger.debug('Success upload - res:%s' % (res))
        self.logger.debug('Success upload - %s (%s bytes)' % (fileName, len(data)))
        return True

    def deleteFile(self, fileItem):
        self.logger.debug('Deleting - \'%s\'' % (fileItem.fileName))
        with self.stopwatch('deleting'):
            try:
                md = self.dbx.files_delete(os.path.join(self.dropboxDir, fileItem.fileName))
            except dropbox.exceptions.ApiError as err:
                raise Exception('%s - API error:%s' % (fileItem.fileName, err))
        self.logger.debug('Success delete - %s' % fileItem.fileName)

    # process helpers
    def fixLocalTimestamps(self):
        for fileName in self.locList:
            self._debugFixLocalTimestamp(fileName)
        self.logger.debug('Timestamps fixed in local files:%s' % len(self.locList))

    def _debugFixLocalTimestamp(self, fileName):
        from datetime import datetime
        basename = os.path.splitext(fileName)[0]
        newTime0 = None
        if "." in basename:
            newTime0 = datetime.strptime(basename, "%Y-%m-%d %H.%M.%S")
        else:
            newTime0 = datetime.strptime(basename, "%Y-%m-%d %H-%M-%S")

        newTime = time.mktime(newTime0.timetuple())
        # self.logger.debug('%s - %s -> %s' % (fileName, newTime0, newTime))
        os.utime(os.path.join(self.localDir, fileName), (newTime, newTime))

    @contextlib.contextmanager
    def stopwatch(self, message):
        """Context manager to print how long a block of code took."""
        t0 = time.time()
        try:
            yield
        finally:
            t1 = time.time()
            self.logger.debug('Total elapsed time for %s: %.3f' % (message, t1 - t0))


