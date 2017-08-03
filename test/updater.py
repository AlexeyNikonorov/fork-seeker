import threading
import time
import socket, cPickle
from multiprocessing import Pipe
from Event import Bookmaker, Event
from WilliamHill import WilliamHill
from Betway import Betway

class Updater(threading.Thread):
    def __init__(self, b):
        threading.Thread.__init__(self)
        self.b = b

    def run(self):
        while True:
            time.sleep(1)
            self.b.update()


if __name__ == '__main__':

    b1 = Betway()
    b1.load_live(); time.sleep(2)
    b1.parse_live(); print b1

    #b2 = WilliamHill()
    #b2.load_live(); time.sleep(2)
    #b2.parse_live()

    Updater(b1).start()
    #Updater(b2).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('',  50007))
    sock.listen(5)

    while True:
        conn, addr = sock.accept()
        s = cPickle.loads(conn.recv(1024))
        print s


