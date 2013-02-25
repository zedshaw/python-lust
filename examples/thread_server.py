import threading
import SocketServer
import sys
from lust import log, server


RUN_DIR="/var/run/threadserver"

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    allow_reuse_address = True

    def handle(self):
        log.info("Connection %r:%r" % self.client_address)
        self.request.sendall("HI!")
        self.request.close()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class ThreadDaemon(server.Simple):

    def before_drop_privs(self, args):
        if not args:
            log.error("You need to list some ports.")
            sys.exit(1)

        HOST = "0.0.0.0"
        ports = (int(x) for x in args)

        self.server = None # this gets the last one to do a forever on

        for PORT in ports:
            server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
            ip, port = server.server_address
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

        self.server = server

    def start(self, args):
        self.server.serve_forever()

    def shutdown(self, signal):
        log.info("Shutting down now signal: %d" % signal)


if __name__ == "__main__":

    server = ThreadDaemon("threadserver", uid='zedshaw', gid='staff')
    server.run(sys.argv)

