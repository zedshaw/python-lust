import pwd
import grp
import signal
import os
import log

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


def daemonize(prog_name, pid_file_path="/var/run"):
    if os.fork() == 0:
        os.setsid()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        pid = os.fork()

        if pid != 0:
            os._exit(0)
        else:
            pid_remove_dead(prog_name, pid_file_path=pid_file_path)
            pid_store(prog_name, pid_file_path=pid_file_path)
    else:
        os._exit(0)


def chroot_jail(root="/tmp"):
    os.chroot(root)
    os.chdir("/")


def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    log.info("Dropping pivs to UID %r GID %r" % (running_uid, running_gid))

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    os.umask(077)


def register_shutdown(handler):
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

