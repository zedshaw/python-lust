from lust import log, server
import os
import sys

def handle(socket, address):
    log.info("Blocking %r:%r" % address)
    socket.close()

class Service(server.Simple):

    name = 'geventserver'

    def before_jail(self, args):
        from gevent.server import StreamServer

        self.host = self.config.get('geventserver.host', '0.0.0.0')
        self.ports = (int(x) for x in self.config['geventserver.ports'].split())
        log.info("Listening ports %r" % self.ports)

        self.server = None # this gets the last one to do a forever on

        for port in self.ports:
            self.server = StreamServer((self.host, port), handle)
            self.server.start()

    def start(self, args):
        self.server.serve_forever()

    def shutdown(self, signal):
        log.info("Shutting down now signal: %d" % signal)

if __name__ == "__main__":

    log.setup('/tmp/geventserver.log')
    server = Service(config_file=os.getcwd() + '/examples/master.conf')
    server.run(sys.argv)

