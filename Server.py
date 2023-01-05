import socket
import threading
import Packets
from Topic import Topic
from Client import Client
import select

CONNECT = 16
PUBLISH_QoS0 = 48
PUBLISH_QoS1 = 50
PUBLISH_QoS2 = 52
PUBACK = 64
SUBSCRIBE = 130
UNSUBSCRIBE = 162
PINGREQ = 192
DISCONNECT = 224



class Server:
    def __init__(self, ip, port):
        self.index = 0
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
                threading.Thread(target=self.packets_handle, args=(conn, addr, self.index)).start()
                self.index += 1
            except:
                print("Eroare la pornirea thread‐ului")

    def packets_handle(self, conn, addr, index):
        client = 0
        while 1:
            try:
                data = conn.recv(1024)
            except:
                for client in self.clients:
                    if conn == Client.getConn(client):
                        Packets.lastWill(self.clients, client.getTopic(), client.getMessage(), client.getQoS())
                break
            if not data:
                break
            for client in self.clients:
                if conn == Client.getConn(client):
                    break
            if data[0] == CONNECT:
                ret = Packets.connect(conn, data, addr)
                if ret != 23:
                    self.clients.append(ret)
                    ret.afisare()
            if data[0] == SUBSCRIBE:
                topic_name = Packets.subscribe(conn, data)
                topic = Topic(topic_name.rstrip("/#"))
                client.sub(topic)
                client.retrigger()
                client.printTopics()

            if data[0] == UNSUBSCRIBE:
                topic_name = Packets.unsubscribe(conn, data)
                client.unsub(topic_name.rstrip("/#"))
                client.retrigger()
                client.printTopics()

            if data[0] == PINGREQ:
                Packets.pingreq(conn)
                client.retrigger()

            if data[0] == PUBLISH_QoS0:
                Packets.publishQoS0(self.clients, data)
                client.retrigger()

            if data[0] == PUBLISH_QoS1:
                print(self.clients)
                clients_receive = Packets.publishQoS1(conn, self.clients, data)
                for cl in clients_receive:
                    Client.setQoS(cl, 1)
                    self.sendQoS1(cl, data)
                client.retrigger()

            if data[0] == PUBACK:
                Client.setQoS(client, 0)
                client.retrigger()

            if data[0] == DISCONNECT:
                self.clients.remove(client)

            print(addr, ' a trimis: ', data)
        conn.close()

    def sendQoS1(self, cl, data):
        timer = threading.Timer(5, self.sendQoS1, args=(cl, data))
        if Client.getQos(cl):
            try:
                Client.getConn(cl).send(data)
            except:
                pass
            timer.start()
        else:
            timer.cancel()

