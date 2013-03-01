import sys
import os
sys.path.append(os.getcwd())
from lust import log, server
import time


RUN_DIR=os.path.join(os.getcwd(), "tests")


class SimpleDaemon(server.Simple):

    def before_daemonize(self, args):
        with open("/tmp/before_daemonize.txt", "w") as f:
            f.write("%r" % args)

    def before_jail(self, args):
        with open("/tmp/before_jail.txt", "w") as f:
            f.write("%r" % args)

    def before_drop_privs(self, args):
        assert os.getcwd() == "/", "CWD is not /, chroot failed."

        with open("before_drop_priv.txt", "w") as f:
            f.write("HI")

    def start(self, args):
        while True:
            time.sleep(1)

    def shutdown(self, signal):
        log.info("Shutting down now signal: %d" % signal)


if __name__ == "__main__":
    # if you're on OSX then change this to whatever user nd group
    server = SimpleDaemon("simpledaemon", uid='zedshaw', gid='staff', 
                          pid_file_path=RUN_DIR, run_base=RUN_DIR, log_dir=RUN_DIR)
    server.run(sys.argv)

