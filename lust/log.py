import sys
import os
import time

DEBUG=False
SETUP=False

# need a simple thread lock on this, or just fuck it

def setup(log_path, force=False):
    global SETUP

    if force: SETUP=False

    if not SETUP:
        # test we can open for writing
        with open(log_path, 'a+') as f:
            f.write("[%s] INFO: Log opened.\n" % time.ctime())

        os.closerange(0, 1024)

        fd = os.open(log_path, os.O_RDWR | os.O_CREAT)

        os.dup2(0, 1)
        os.dup2(0, 2)

        sys.stdout = os.fdopen(fd, 'a+', 0)
        sys.stderr = sys.stdout
        SETUP=True

def warn(msg):
    print "[%s] WARN: %s" % (time.ctime(), msg)


def error(msg):
    print "[%s] ERROR: %s" % (time.ctime(), msg)


def info(msg):
    print "[%s] INFO: %s" % (time.ctime(), msg)


def debug(msg):
    if not DEBUG:
        print "[%s] DEBUG: %s" % (time.ctime(), msg)


def set_debug_level(on):
    global DEBUG
    DEBUG=on

