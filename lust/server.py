from . import unix, log, config
import sys
import os

class Simple(object):

    name = None
    should_jail = True
    should_drop_priv = True

    def __init__(self, run_base="/var/run", log_dir="/var/log",
                 pid_file_path="/var/run",
                 uid="nobody", gid="nogroup", config_file=None):
        assert self.name, "You must set the service's name."

        config_file = config_file or os.path.join('/etc', self.name + ".conf")
        self.load_config(config_file)
        self.run_dir = self.get('run_dir') or os.path.join(run_base, self.name)
        self.pid_path = self.get('pid_path') or pid_file_path
        self.log_file = self.get('log_file') or os.path.join(log_dir, self.name + ".log")
        self.uid = self.get('uid') or uid
        self.gid = self.get('gid') or gid
        self.run_dir_mode = self.get('run_dir_mode') or '0700'
        self.run_dir_mode = int(self.run_dir_mode, 8)

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

        if not os.path.exists(self.run_dir):
            log.warn("Directory %s does not exist, attempting to create it." %
                     self.run_dir)
            os.mkdir(self.run_dir)

            log.info("Giving default permissions to %s, change them later if you need."
                     % self.run_dir)
            os.chown(self.run_dir, self.unum, self.gnum)
            os.chmod(self.run_dir, self.run_dir_mode)

        if self.should_jail:
            self.before_jail(args)
            log.info("Setting up the chroot jail to: %s" % self.run_dir)
            unix.chroot_jail(self.run_dir)
        else:
            log.warn("This daemon does not jail itself, chdir to %s instead" % self.run_dir)
            os.chdir(self.run_dir)

        if self.should_drop_priv:
            self.before_drop_privs(args)
            unix.drop_privileges(self.unum, self.gnum)
        else:
            log.warn("This daemon does not drop privileges.")

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

    def load_config(self, config_file):
        self.config_file = config_file
        log.debug("Config file at %s" % self.config_file)

        if os.path.exists(self.config_file):
            self.config = config.load_ini_file(self.config_file)
            log.debug("Loading config file %s contains %r" % (self.config_file,
                                                              self.config))
        else:
            log.warn("No config file at %s, using defaults." % self.config_file)
            self.config = {}

