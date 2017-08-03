import socket
import random, time
import threading

class Listeners(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('',  50007))
        self.sock.listen(5)
        self.listeners = []
    def send(self, data):
        while True:
            try:
                listener = self.listeners.pop()
                listener.send(data)
                listener.close()
            except socket.error:
                continue
            except IndexError:
                break
    def run(self):
        while True:
            try:
                conn, addr = self.sock.accept()
                print 'listener connected'
                self.listeners.append(conn)
            except socket.error:
                break

def translate():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('',  50006))
    sock.listen(5)

    listeners = Listeners()
    listeners.start()
    try:
        while True:
            conn, addr = sock.accept()
            data = conn.recv(1024)
            conn.close()
            listeners.send(data)
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        time.sleep(2)

if __name__ == '__main__':
    translate()


