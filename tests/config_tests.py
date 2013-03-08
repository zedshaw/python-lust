from nose.tools import *
from lust import config

def test_load_ini_file():
    settings = config.load_ini_file("tests/sample.ini")
    assert_equal(settings['threadserver.run_dir'], '/var/run/threadserver')

def test_load_ini_file_defaults():
    settings = config.load_ini_file("tests/sample.ini", defaults={'threadserver.run_dir':
                                                                  '/var/other'})
    assert_equal(settings['threadserver.run_dir'], '/var/other')

