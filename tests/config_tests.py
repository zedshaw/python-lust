from nose.tools import *
from lust import config

def test_load_ini_file():
    settings = config.load_ini_file("tests/sample.ini")
    assert_equal(settings['mysqld.user'], 'mysql')
    assert_equal(settings['mysqld.pid-file'], '/var/run/mysqld/mysqld.pid')
    assert_equal(settings['mysqld.old_passwords'], '1')

