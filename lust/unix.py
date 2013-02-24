import pwd
import grp
import signal
import os
import log

def make_pid_file_path(name, pid_file_path):
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
            pid = int(f.read())
            log.warn("Old process running at %d" % pid)
            return pid
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
            log.warn("Process really running at %d" % pid)
            return True
        except OSError:
            # this means the process is gone
            log.warn("Stale pid file %r has %d pid." % (
                make_pid_file_path(name, pid_file_path), pid))
            return False


def pid_remove_dead(name, pid_file_path="/var/run"):
    if not still_running(name, pid_file_path=pid_file_path):
        os.remove(make_pid_file_path(name, pid_file_path))


def daemonize(prog_name, pid_path="/var/run"):
    if os.fork() == 0:
        os.setsid()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        pid = os.fork()

        if pid != 0:
            os._exit(0)
        else:
            pid_remove_dead(prog_name, pid_path)
            pid_store(prog_name, pid_path)
    else:
        os._exit(0)


def chroot_jail(root="/tmp"):
    os.chroot(root)


def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

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

