#!/usr/bin/python

import os
import logging
import logging.handlers
import tempfile

"""
Logger helper
"""


def defaultLogFilePath(fileName):
    """ Return temporary filepath with script name. use with __file__ """
    scriptname = os.path.splitext(os.path.basename(fileName))[0]
    tempdir = tempfile.gettempdir()
    return os.path.join(tempdir, scriptname + '.log')

def createLogFileHandler(filePath, maxBytes=1048576, backupCount=3):
    fileHandler = logging.handlers.RotatingFileHandler(filePath, maxBytes=maxBytes, backupCount=backupCount)
    formatDt = u"%Y-%m-%d %H:%M:%S"
    fmtFile = logging.Formatter(fmt=u"%(asctime)s.%(msecs)-3d %(module)-15s %(levelname)-7s %(message)s", datefmt=formatDt)
    fileHandler.setFormatter(fmtFile)
    return fileHandler

def createConsoleHandler():
    conHandler = logging.StreamHandler()
    conHandler.setLevel(logging.DEBUG)
    fmtCon = logging.Formatter(fmt=u"%(asctime)s %(message)s", datefmt=u"%H:%M:%S")
    conHandler.setFormatter(fmtCon)
    return conHandler

def createFileRotationHandler(filePath, maxBytes=1048576, backupCount=3):
    handler = logging.handlers.RotatingFileHandler(filePath, maxBytes=maxBytes, backupCount=backupCount)
    return handler


