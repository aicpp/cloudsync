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

        the_args = vars(args)
        db_dir = Path(the_args['dropboxdir'])
        local_dir = Path(the_args['localdir'])



        for root, dirs, files in os.walk(the_args['localdir']):
            local_path = Path(root)
            db_path = db_dir / local_path.relative_to(local_dir)
            for folder in dirs:
                the_args['localdir'] = str(local_path / folder)
                the_args['dropboxdir'] = str(db_path / folder)
                dbSync = dropboxsync.DropboxSync(**the_args)
                dbSync.setLogger(logger)
                dbSync.prepare()

                filters = FilterParameters()
                filters.days = dbSync.args['match_days']
                dbSync.filterSourceFiles(filters)

                dbSync.synchronize()
        the_args['localdir'] = str(local_dir)
        the_args['dropboxdir'] = str(db_dir)

        dbSync = dropboxsync.DropboxSync(**the_args)
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

