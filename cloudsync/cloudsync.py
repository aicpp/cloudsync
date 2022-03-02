#!/usr/bin/python

import os
from pathlib import Path
import sys

import dropboxsync
import logging
import logger as lgr
import argparse

from sync_file.filters import FilterParameters


def isCronMode():
    return not os.isatty(sys.stdin.fileno())

#configure logger
def createLogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not isCronMode():
        logger.setLevel(logging.DEBUG)
        logger.addHandler(lgr.createConsoleHandler())
    logFilePath = lgr.defaultLogFilePath(__file__)
    logger.addHandler(lgr.createLogFileHandler(logFilePath))
    return logger

def createParser():
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Sync files between local directory and Dropbox (in both directions)')
    parser.add_argument('--dropboxdir', required=True,
                        help='Directory in your Dropbox')
    parser.add_argument('--localdir', required=True,
                        help='Local directory')
    parser.add_argument('--direction', required=True, choices=['todropbox','tolocal'],
                        help='Direction to sync')
    parser.add_argument('--token', required=True,
                        help='Access token (see https://www.dropbox.com/developers/apps)')

    # additional filtration
    parser.add_argument('--match-days', nargs='?', type=int,
                        help='Copy only newer files (file modification time is newer last N-days)')
    return parser

def main():

    parser = createParser()
    args = parser.parse_args()

    logger = createLogger()
    # logger.debug("isCron:%s" % isCronMode())
    # logger.debug('vars:%s' % vars(args))
    # sys.exit(0)

    # parse token
    if not args.token:
        logger.error('--token is mandatory')
        sys.exit(2)

    try:

        dbSync = dropboxsync.DropboxSync(**vars(args))
        dbSync.setLogger(logger)
        dbSync.prepare()

        filters = FilterParameters()
        filters.days = dbSync.args['match_days']
        dbSync.filterSourceFiles(filters)

        dbSync.synchronize()


    except:
        logger.exception('')


if __name__ == '__main__':
    main()

