from nose.tools import *
from lust import unix
import os
from time import sleep

def setup():
    if unix.still_running("simpledaemon", pid_file_path="tests"):
        os.system('sudo python tests/simple_test_server.py stop')


def test_simple_server():
    if not os.path.exists("tests/simpledaemon"):
        os.mkdir("tests/simpledaemon")

    os.system('sudo python tests/simple_test_server.py start')
    sleep(1)

    EXPECT_PATHS=['tests/simpledaemon.pid',
                  'tests/simpledaemon.log',
                  'tests/simpledaemon/before_drop_priv.txt',
                  '/tmp/before_jail.txt',
                  '/tmp/before_daemonize.txt']

    for path in EXPECT_PATHS:
        assert_true(os.path.exists(path), "File %s not there." % path)

    os.system('sudo python tests/simple_test_server.py stop')
    sleep(1)

    assert_false(unix.still_running("simpledaemon", pid_file_path="tests"))
