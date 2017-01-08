import asyncore
import cec
import socket
import subprocess


def cec_set_power_state(device, on):
    if on:
        device.power_on()
    else:
        device.standby()


class DummyHandler(asyncore.dispatcher):
    def __init__(self, server, *args, **kwargs):
        asyncore.dispatcher.__init__(self, *args, **kwargs)
        self.server = server

    def handle_read(self):
        self.recv(8192)

    def handle_close(self):
        self.close()
        self.server.conn_closed()


class WoLServer(asyncore.dispatcher):
    def __init__(self, host, port, device):
        asyncore.dispatcher.__init__(self)

        self.connections = 0
        self.device = device

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

        addr = self.socket.getsockname()
        print "Listening on %s!" % (addr,)

        subprocess.Popen(["avahi-publish", "--service", "tv-wol", "_tv-wol._tcp", str(addr[1])])

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            print("New connection from %s" % pair)
            self.connections += 1
            self.update_power_state()
            sock, addr = pair
            DummyHandler(self, sock)

    def conn_closed(self):
        print("Connection dropped")
        self.connections -= 1
        self.update_power_state()

    def update_power_state(self):
        if self.connections == 0:
            print("Turning on...")
            cec_set_power_state(device=self.device, on=False)
            print("DONE")
        elif self.connections == 1:
            print("Turning off...")
            cec_set_power_state(device=self.device, on=True)
            print("DONE")


def main():
    cec.init()

    WoLServer('0.0.0.0', 0, cec.Device(0))
    asyncore.loop()


if __name__ == '__main__':
    main()
