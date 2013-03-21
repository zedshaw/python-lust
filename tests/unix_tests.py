from nose.tools import *
from lust import unix, log
from mock import patch, Mock
import sys
import os
import time
import signal

# These tests use mocks to avoid system calls, with testing that the
# functionality works in the tests/server_tests.py using small server
# that are launched and confirmed work.

def test_make_pid_file_path():
    path = unix.make_pid_file_path("testing")
    assert_equal(path, "/var/run/testing.pid")
    path = unix.make_pid_file_path("testing", pid_file_path="/var/run/stuff")
    assert_equal(path, "/var/run/stuff/testing.pid")


def test_pid_store():
    unix.pid_store("testing", pid_file_path="/tmp")
    assert_equal(os.path.exists("/tmp/testing.pid"), True,
                           "Didn't make /tmp/testing.pid")
    os.unlink("/tmp/testing.pid")

def test_pid_read():
    unix.pid_store("test_pid_read", pid_file_path="/tmp")
    pid = unix.pid_read("test_pid_read", pid_file_path="/tmp")
    assert_equal(pid, os.getpid())
    os.unlink("/tmp/test_pid_read.pid")

def test_still_running():
    unix.pid_store("test_still_running", pid_file_path="/tmp")
    assert_true(unix.still_running("test_still_running", pid_file_path="/tmp"))
    os.unlink("/tmp/test_still_running.pid")

@patch("os.kill", new=Mock(side_effect=OSError))
def test_still_running_stale_process():
    unix.pid_store("test_still_running", pid_file_path="/tmp")
    assert_false(unix.still_running("test_still_running", pid_file_path="/tmp"))
    os.unlink("/tmp/test_still_running.pid")

@patch("lust.unix.still_running", new=Mock(return_value=False))
def test_pid_remove_dead():
    unix.pid_store("test_pid_remove_dead", pid_file_path="/tmp")
    unix.pid_remove_dead("test_pid_remove_dead", pid_file_path="/tmp")
    assert_false(os.path.exists("/tmp/test_pid_remove_dead.pid"))

@patch("lust.unix.still_running", new=Mock(return_value=True))
def test_pid_remove_dead_still_running():
    unix.pid_store("test_pid_remove_dead", pid_file_path="/tmp")
    unix.pid_remove_dead("test_pid_remove_dead", pid_file_path="/tmp")
    assert_true(os.path.exists("/tmp/test_pid_remove_dead.pid"))

@patch("os.kill")
def test_signal_server(os_kill):
    unix.pid_store("test_signal_server", pid_file_path="/tmp")
    unix.kill_server("test_signal_server", pid_file_path="/tmp")
    assert_true(os_kill.called)
    os_kill.reset

    unix.reload_server("test_signal_server", pid_file_path="/tmp")
    assert_true(os_kill.called)
    os_kill.reset

    os.unlink("/tmp/test_signal_server.pid")


@patch("lust.unix.still_running", new=Mock(return_value=False))
@patch("os.fork", new=Mock(return_value=0))
@patch("os.setsid")
@patch("signal.signal")
@patch("os._exit")
def test_daemonize(os__exit, *calls):
    unix.daemonize("test_daemonize", pid_file_path="/tmp")

    for i in calls:
        assert_true(i.called, "Failed to call %r" % i)

    # should not be calling exit
    assert_false(os__exit.called)

def test_daemonize_dont_exit():
    os.unlink('/tmp/test_daemonize_no_exit.log')
    os.unlink('/tmp/test_daemonize_no_exit.pid')

    def main():
        """This will exit the daemon after 4 seconds."""
        log.setup('/tmp/test_daemonize_no_exit.log', force=True)
        for i in range(0, 4):
            log.info("I ran!")
            time.sleep(1)

    unix.daemonize('test_daemonize_no_exit', pid_file_path="/tmp",
                         dont_exit=True, main=main)

    while not unix.still_running('test_daemonize_no_exit', pid_file_path='/tmp'):
        time.sleep(1)

    assert_true(os.path.exists('/tmp/test_daemonize_no_exit.pid'))


@patch("os.chroot")
def test_chroot_jail(chroot_jail):
    unix.chroot_jail()
    assert_true(chroot_jail.called, "Failed to call the chroot jail.")


@patch("pwd.getpwnam")
@patch("grp.getgrnam")
@patch("os.setgroups")
@patch("os.setgid")
@patch("os.setuid")
@patch("os.umask")
@patch("os.getuid")
def test_drop_privileges(os_getuid, *calls):
    # fakes out os.getuid to claim it's running as root
    os_getuid.return_value = 0

    unix.drop_privileges()

    # now just confirm all the remaining system calls were called
    for i in calls:
        assert_true(i.called, "Failed to call %r" % i)


@patch("os.getuid")
@patch("pwd.getpwnam")
def test_drop_privileges_not_root(pwd_getpwnam, os_getuid):
    # fakes out os.getuid to claim it's running as root
    os_getuid.return_value = 1000
    unix.drop_privileges()

    assert_true(os_getuid.called)
    assert_false(pwd_getpwnam.called)

@patch("signal.signal")
def test_register_shutdown(signal_signal):
    def dummy_handler(signal, frame):
        pass

    unix.register_shutdown(dummy_handler)

    assert_true(signal_signal.called)


