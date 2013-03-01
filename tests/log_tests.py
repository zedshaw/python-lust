from nose.tools import *
from lust import log
from mock import *


@patch("sys.stdout")
@patch("sys.stderr")
@patch("os.close")
@patch("os.dup2")
@patch("os.fdopen")
def test_setup(*calls):
    log.setup("tests/test.log")
    # confirm the last three in the @path list are called
    for i in calls[0:3]:
        assert_true(i.called, "Did not call %r" % i)


@patch('time.ctime')
def test_message_levels(time_ctime):
    log.warn("test warning")
    assert_true(time_ctime.called)
    time_ctime.reset

    log.error("test error")
    assert_true(time_ctime.called)
    time_ctime.reset

    log.info("test info")
    assert_true(time_ctime.called)
    time_ctime.reset


@patch('time.ctime')
def test_debug_level(time_ctime):
    log.set_debug_level(True)
    assert_true(log.DEBUG, "DEBUG should be true.")
    log.debug("Test")
    assert_false(time_ctime.called, "Should not get called.")
    log.set_debug_level(False)
    assert_false(log.DEBUG, "DEBUG should be true.")
    log.debug("Test")
    assert_true(time_ctime.called, "Should get called.")

