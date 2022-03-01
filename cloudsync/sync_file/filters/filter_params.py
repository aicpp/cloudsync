from datetime import datetime, timedelta
import re
import time


class FilterParameters:

    def __init__(self):
        self._days = None
        self._size = None
        self._name_regexes = [
            re.compile('^\\..+|/\\..+'),  # match hidden files
            re.compile('^~.*|/~.*'),  # match temporary files
        ]

    @property
    def days(self):
        return self._days

    @days.setter
    def days(self, val: int):
        self._days = val

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, val: int):
        self._size = val

    def filter_name(self, file_name: str) -> bool:
        for reg in self._name_regexes:
            if reg.match(file_name):
                return True
        return False

    def filter_days(self, file_mod: int) -> bool:
        if self._days is None:
            return False

        threshold_day = time.mktime((datetime.today() - timedelta(days=self.days)).timetuple())

        return threshold_day < file_mod

    def filter_size(self, file_size: int) -> bool:
        return self.size > file_size
