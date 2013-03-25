import pwd
import grp
import signal
import os
from . import log

def make_pid_file_path(name, pid_file_path="/var/run"):
    return os.path.join(pid_file_path, name + ".pid")

def pid_store(name, pid_file_path="/var/run"):
    os.umask(077) # set umask for pid
    pid_path = make_pid_file_path(name, pid_file_path)

    with open(pid_path, "w") as f:
        f.write(str(os.getpid()))


def pid_read(name, pid_file_path="/var/run"):
    pid_path = make_pid_file_path(name, pid_file_path)
    log.debug("Checking pid path: %s" % pid_path)

    try:
        with open(pid_path, "r") as f:
            return int(f.read())
    except IOError:
        return -1

def still_running(name, pid_file_path="/var/run"):
    pid = pid_read(name, pid_file_path=pid_file_path)

    if pid == -1:
        log.debug("Returned pid not running at %s" % pid)
        return False
    else:
        # check if the process is still running with kill
        try:
            os.kill(pid, 0)
            log.debug("Process running at %d" % pid)
            return True
        except OSError:
            # this means the process is gone
            log.warn("Stale pid file %r has %d pid." % (
                make_pid_file_path(name, pid_file_path), pid))
            return False


def kill_server(name, pid_file_path="/var/run", sig=signal.SIGINT):
    if still_running(name, pid_file_path=pid_file_path):
        pid = pid_read(name, pid_file_path=pid_file_path)
        os.kill(pid, sig)


def reload_server(name, pid_file_path="/var/run"):
    kill_server(name, pid_file_path=pid_file_path, sig=signal.SIGHUP)


def pid_remove_dead(name, pid_file_path="/var/run"):
    if not still_running(name, pid_file_path=pid_file_path):
        pid_file = make_pid_file_path(name, pid_file_path)
        if os.path.exists(pid_file):
            os.remove(pid_file)


def daemonize(prog_name, pid_file_path="/var/run", dont_exit=False, main=None):
    """
    This will do the fork dance to daemonize the Python script.  You have a
    couple options in using this.
    
    1) Call it with just a prog_name and the current script forks like normal
    then continues running.

    2) Add dont_exit=True and it will both fork a new process *and* keep the
    parent.

    3) Set main to a function and that function will become the new main method
    of the process, and the process will exit when that function ends.
    """
    if os.fork() == 0:
        os.setsid()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        pid = os.fork()

        if pid != 0:
            os._exit(0)
        else:
            pid_remove_dead(prog_name, pid_file_path=pid_file_path)
            pid_store(prog_name, pid_file_path=pid_file_path)

            if main: 
                main()
                os._exit(0)

    elif dont_exit:
        return True
    else:
        os._exit(0)


def chroot_jail(root="/tmp"):
    os.chroot(root)
    os.chdir("/")


def get_user_info(uid, gid):
    return (
        pwd.getpwnam(uid).pw_uid,
        grp.getgrnam(gid).gr_gid,
    )


def drop_privileges(running_uid, running_gid):
    if os.getuid() != 0:
        return

    log.info("Dropping pivs to UID %r GID %r" % (running_uid, running_gid))

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    os.umask(077)


def register_signal(handler, signals):
    for sig in signals:
        signal.signal(sig, handler)


def register_shutdown(handler):
    register_signal(handler, signals=[signal.SIGINT, signal.SIGTERM])

