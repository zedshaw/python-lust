from lust import unix, log
import sys
import os

class Simple(object):

    def __init__(self, name, run_base="/var/run", log_dir="/var/log",
                 uid="nobody", gid="nogroup"):
        self.name = name
        self.run_dir = os.path.join(run_base, self.name)
        self.log_file = os.path.join(log_dir, self.name + ".log")
        self.uid = uid
        self.gid = gid

    def before_daemonize(self, args):
        pass

    def before_jail(self, args):
        pass

    def before_drop_privs(self, args):
        pass

    def start(self, args):
        pass


    def stop(self, args):
        log.info("Stopping server.")
        unix.kill_server(self.name)


    def status(self, args):
        print "Server running at pid %d" % unix.pid_read(self.name)


    def shutdown(self, signal):
        pass


    def clear_pid(self):
        try:
            os.remove(unix.make_pid_file_path(self.name))
        except OSError:
            pass
        sys.exit(0)


    def parse_cli(self, args):
        args.pop(0)
        return args[0], args[1:]


    def daemonize(self, args):
        log.setup(self.log_file)
        log.info("Daemonizing.")

        self.before_daemonize(args)

        if unix.still_running(self.name):
            log.error("%s still running. Aborting." % self.name)
            sys.exit(1)
        else:
            unix.daemonize(self.name)

        def shutdown_handler(signal, frame):
            self.shutdown(signal)
            self.clear_pid()

        unix.register_shutdown(shutdown_handler)

        self.before_jail(args)

        log.info("Setting up the chroot jail to: %s" % self.run_dir)
        unix.chroot_jail(self.run_dir)

        self.before_drop_privs(args)

        log.info("Server %s running." % self.name)
        unix.drop_privileges(uid_name=self.uid, gid_name=self.gid)

        self.start(args)


    def run(self, args):
        command, args = self.parse_cli(args)

        if command == "start":
            self.daemonize(args)
        elif command == "stop":
            self.stop(args)
        elif command == "status":
            self.status(args)
        else:
            log.error("Invalid command: %s.  Commands are: start, stop, reload, status.")
            sys.exit(1)
    
