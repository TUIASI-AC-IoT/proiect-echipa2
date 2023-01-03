import socket
import threading
import Packets

CONNECT = 16
SUBSCRIBE = 130
UNSUBSCRIBE = 162
PINGREQ = 192

class Server:
    def __init__(self, ip, port):
        index=0
        self.clients = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))
        self.socket.listen(5)
        print('Asteapta conexiuni (oprire server cu Ctrl‐C)')
        while 1:
            try:
                conn, addr = self.socket.accept()
            except KeyboardInterrupt:
                print("Bye bye")
                break
            try:
                threading.Thread(target=self.packets_handle, args=(conn, addr, index)).start()
                index += 1
            except:
                print("Eroare la pornirea thread‐ului")

    def packets_handle(self, conn, addr, index):
        while 1:
            try:
                data = conn.recv(1024)
            except:
                break
            if not data:
                break
            if data[0] == CONNECT:
                ret = Packets.connect(conn, data, addr)
                if ret != 23:
                    self.clients.append(ret)
                    self.clients[index].afisare()
            if data[0] == SUBSCRIBE:
                Packets.subscribe(conn, data)
                self.clients[index].retrigger()

            if data[0] == UNSUBSCRIBE:
                Packets.unsubscribe(conn, data)
                self.clients[index].retrigger()

            if data[0] == PINGREQ:
                Packets.pingreq(conn)
                self.clients[index].retrigger()

            print(addr, ' a trimis: ', data)
        conn.close()
