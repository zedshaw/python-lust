import pwd
import grp
import signal
import os

def pid_store(pid_file_path, name):
    os.umask(077) # set umask for pid
    save_to = os.path.join(pid_file_path, name)

    with open(save_to, "w") as f:
        f.write(str(os.getpid()))


def pid_read(pid_file_path, name):
    pass


def still_running(pid_file_path, name):
    pass


def pid_remove_dead(pid_file_path, name):
    pass


def daemonize(pid_path="/var/run"):
    if os.fork() == 0:
        os.setsid()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        pid = os.fork()

        if pid != 0:
            os._exit(0)
        else:
            pid_store(pid_path, "dentata.pid")
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
    pass

