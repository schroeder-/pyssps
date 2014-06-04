# In diesem File werden Server und Client für TCP Verbindungen bereit gestellt
# diese stellt den Datenbuss der SPS zu extern Komponenten dar
# Die SPS läuft als TCP Client mit den einzelen IOs kommunziert sind die IOs
# auf einem PC müssen unterschiedliche Ports verwendet werden.
# Die IOs laufen als Server.
#
# Die gesendten Packete sind wie folgt aufgebaut:
# 0..4 4Byte Länge in Daten Sätzen
# Nun folgen immer zwei Byte pro Satz Daten
# 4Byte Addresse
# 4Byte Wert
import socketserver
import select
import socket
import struct
import threading
import queue
#@TODO Reconnects client
#test
#abrüche simulieren
#vieles mehr

#Die Klasse wird für jede Verbindung instansiert
class IOHandler(socketserver.BaseRequestHandler):
    #Wird beim benndeten aufgerufen benndet den Nebläufengen thread
    #der Änderungen sendet
    def finish(self):
        self.stop_event.set()
        self.t.join()
        self.server.q_lock.acquire()
        self.server.queues.remove(self.q)
        self.server.q_lock.release()

    #Hier wird auf ankommende Nachrichten gewartet
    #Handle wird immer nach setup() automatisch aufgerufen
    def handle(self):
        while True:
            inputs = [self.request]
            try:
                in_rdy, _, _ = select.select(inputs, [], [])
            except socket.error:
                break
            except select.error:
                break
            data = self.request.recv(4096)
            if data == b'':
                break
            tmp = []
            for i in range(0, len(data),  4):
                #Rückwandlung von Byte in Integer
                tmp.append(struct.unpack('!l', data[i:i+4])[0])
            data = tmp
            size = data[0]
            data = data[1:]
            addr_val = []
            for i in range(0, size, 2):
                addr_val.append((data[i], data[i+1]))
            self.server.io.con_flash(addr_val)

            
    #Wird beim Starten der Verbindung aufgerufen
    #Bereitet Threads und Queues sowie Locks vor
    def setup(self):
        print('connection ')
        self.stop_event = threading.Event()
        self.server.q_lock.acquire()
        self.q = queue.Queue()
        self.server.queues.append(self.q)
        self.server.q_lock.release()
        self.server.io.init_con()
        self.t = threading.Thread(target=self.send_th)
        self.t.daemon = True
        self.t.start()

    #Sendet Daten wenn vorhanden
    def send_th(self):
        while True:
            if self.stop_event.isSet():
                break
            try:
                data = self.q.get(True, 0.01)
                self.request.sendall(data)
                self.q.task_done()
            except queue.Empty:
                pass


#Serverclasse
class TcpConServer:
    def __init__(self, io, port):
        host = "localhost"
        self.server = socketserver.TCPServer((host, port), IOHandler)
        io.con = self
        self.server.io = io
        self.server.queues = []
        self.server.q_lock = threading.Lock()
        self.t = threading.Thread(target=self.server.serve_forever)
        self.t.daemon = True
        self.t.start()


#@TODO stop server
    def kill(self):
        pass

    def send(self, addr_val):
        b = bytearray()
        b += len(addr_val).to_bytes(4, 'big')
        for ad, val in addr_val:
            b += ad.to_bytes(4, 'big') + val.to_bytes(4, 'big')
        self.server.q_lock.acquire()
        for q in self.server.queues:
            q.put(b)
        self.server.q_lock.release()

class TcpConClient:
    def __init__(self, io, ip, port):
        self.t = threading.Thread(target=self.con)
        self.t.daemon = True
        self.stop = False
        self.t.start()
        self.io = io
        self.io.con = self
        self.ip = ip
        self.port = port

    def kill(self):
        self.stop =True

#@TODO Timeout um thread bennden sicher zustellen
    #Hier 
    def con(self):
        self.s = None
        while True:
            if self.stop:
                break
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.ip, self.port))
            self.io.init_con()
            while True:
                if self.stop:
                    break
                data = self.s.recv(4096)
                if len(data) == 0:
                    break
                tmp = []
                for i in range(0, len(data),  4):
                    tmp.append(struct.unpack('!l', data[i:i+4])[0])
                data = tmp
                size = data[0]
                data = data[1:]
                addr_val = []
                for i in range(0, size, 2):
                    addr_val.append((data[i], data[i+1]))
                self.io.con_flash(addr_val)
            self.s.close()
            self.s = None

    #Sendet Daten
    def send(self, addr_val):
        b = bytearray()
        b += len(addr_val).to_bytes(4, 'big')
        for ad, val in addr_val:
            b += ad.to_bytes(4, 'big') + val.to_bytes(4, 'big')
        if self.s != None:
            self.s.sendall(b)
