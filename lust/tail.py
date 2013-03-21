import time
import os
import re
from . import log

def file_rotated(file_name, orig_stat):
    while True:
        try:
            new_stat = os.stat(file_name)

            if orig_stat == None:
                return True, new_stat
            elif orig_stat.st_ino != new_stat.st_ino:
                return True, new_stat
            else:
                return False, orig_stat
        except OSError:
            time.sleep(0.1)


def tail_lines(file_name):
    _, orig_stat = file_rotated(file_name, None)
    log_file = open(file_name)
    log_file.seek(0, os.SEEK_END)

    while True:
        line = log_file.readline()
        if line:
            yield line
        else:
            time.sleep(0.1)

            # check for rotation and reopen if it did
            rotated, orig_stat = file_rotated(file_name, orig_stat)
            if rotated:
                log.info("Log file %s rotated." % file_name)
                log_file.close()
                log_file = open(file_name)

def convert_patterns(patterns):
    results = {}

    for pattern, target in patterns.items():
        matcher = re.compile(pattern)
        results[matcher] = target

    return results

def scan_lines(file_name, patterns):
    patterns = convert_patterns(patterns)

    for line in tail_lines(file_name):
        for pattern, target in patterns.items():
            matches = pattern.match(line)
            if matches:
                yield target, line, matches.groupdict()

