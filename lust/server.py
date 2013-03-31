from . import unix, log, config
import sys
import os

class Simple(object):

    name = None

    def __init__(self, run_base="/var/run", log_dir="/var/log",
                 pid_file_path="/var/run",
                 uid="nobody", gid="nogroup", config_file=None):
        assert self.name, "You must set the service's name."

        self.config_file = config_file or os.path.join('/etc', self.config + ".conf")
        log.debug("Config file at %s" % self.config_file)

        if os.path.exists(self.config_file):
            self.config = config.load_ini_file(self.config_file)
            log.debug("Loading config file %s contains %r" % (self.config_file,
                                                              self.config))
        else:
            log.warn("No config file at %s, using defaults." % self.config_file)
            self.config = {}

        self.run_dir = self.config.get(self.name + '.run_dir',
                                       os.path.join(run_base, self.name))
        self.pid_path = self.config.get(self.name + '.pid_path', pid_file_path)
        self.log_file = self.config.get(self.name + '.log_file',
                                        os.path.join(log_dir, self.name + ".log"))
        self.uid = self.config.get(self.name + '.uid', uid)
        self.gid = self.config.get(self.name + '.gid', gid)
        log.debug("UID and GID are %s:%s" % (self.uid, self.gid))

        self.unum, self.gnum = unix.get_user_info(self.uid, self.gid)
        log.debug("Numeric UID:GID are %d:%d" % (self.unum, self.gnum))


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
        unix.kill_server(self.name, pid_file_path=self.pid_path)


    def status(self, args):
        print "Server running at pid %d" % unix.pid_read(self.name,
                                                         pid_file_path=self.pid_path)


    def shutdown(self, signal):
        pass



    def parse_cli(self, args):
        args.pop(0)

        if not args:
            log.error("Need a command like start, stop, status.")
            sys.exit(1)

        return args[0], args[1:]


    def daemonize(self, args):
        log.setup(self.log_file)
        log.info("Daemonizing.")

        self.before_daemonize(args)

        if unix.still_running(self.name, pid_file_path=self.pid_path):
            log.error("%s still running. Aborting." % self.name)
            sys.exit(1)
        else:
            unix.daemonize(self.name, pid_file_path=self.pid_path)

        def shutdown_handler(signal, frame):
            self.shutdown(signal)
            sys.exit(0)

        unix.register_shutdown(shutdown_handler)

        self.before_jail(args)

        log.info("Setting up the chroot jail to: %s" % self.run_dir)
        unix.chroot_jail(self.run_dir)

        self.before_drop_privs(args)

        unix.drop_privileges(self.unum, self.gnum)

        log.info("Server %s running." % self.name)
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

    def get(self, name):
        """Simple convenience method that just uses the service's configured
        name to get a config value."""

        return self.config.get(self.name + '.' + name, None)

