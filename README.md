Sync files to/from Dropbox folder
=================================

The script `cloudsync.py` uses Dropbox API v2 (https://github.com/dropbox/dropbox-sdk-python) to synchronize files between local and Dropbox folders
It uses several filters of files, defined in `filters.py`
* `FileFilterMask` - exclude temporary files by mask. By default: `.*, ~*, thumbs.db`
* `FileFilterDays` - match only files with modification time newer than matchDays days. By default: no filtration.
Each file compare using name, size and modification time to prevent unnecessary synchronization.

Requirements
============
Dropbox account 
Python 2.7 and above 

_Tested on debian wheezy/Mac OS X_

Installation
============

1) Clone this git repo: `git clone https://github/aicpp/cloudsync` 

2) Install Dropbox SDK (see: https://github.com/dropbox/dropbox-sdk-python)

3) Create Dropbox application and get access token

4) Create your own script using your token follow on examples below

Usage
=====
Script log to console and file `/tmp/cloudsync.log` 
Script detect if it run by cron and disable console output in that case.  


Command line arguments
----------------------

**Required params**

`--token` - your dropbox token (see: https://dropbox.com/developers/apps) 
`--dropboxdir` - dropbox directory 
`--localdir` - local directory 
`--direction` - direction of syncronization 
`tolocal` - from Dropbox directory to local directory 
`todropbox` - from local directory to Dropbox directory   

**Optional params**
`--match-days` - copy only files which modification time is newer than `--match-days` days 

Example
-------

Copy photos created in the last 30 days from Dropbox to local directory. Local directory should exists.
```bash
#!/bin/bash

./cloudsync.py \
    --token "YOUR_DROPBOX_ACCESS_TOKEN" \
    --dropboxdir "/Camera Uploads" \
    --localdir ~/dropbox_photos \
    --direction "tolocal" \
    --match-days 30
```

Copy photos from local directory (for example mounted yandex.disk as davfs) to Dropbox directory.
```bash
#!/bin/bash

./cloudsync.py \
    --token "YOUR_DROPBOX_ACCESS_TOKEN" \
    --localdir /mnt/yadisk/diskphotos/Фотокамера \
    --dropboxdir "/YandexPhotos" \
    --direction "todropbox" \
    --match-days 30
```


What script do
--------------
* Copy files from one local directory to target Dropbox directory
* Copy only in one direction, defined in command line argument `--direction`
* Doesn't modify source folder, create/delete file only in target folder
* Filter files with several filters

What script don't do
--------------------
* Doesn't sync subfolders
* Doesn't sync in both directions by one configuration
* Doesn't create target folder

