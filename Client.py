from Topic import *
import threading
import Packets

class Client:
    def __init__(self, conn, addr, client_id, user, password, qos, expiry, will_delay, willtop, willmsg, clean_fl, keep_alive):
        self.topics = []
        self.conn = conn
        self.addr = addr
        self.client_id = client_id
        self.user_name = user
        self.password = password
        self.expiry = expiry
        self.QoS = qos
        self.will_delay = will_delay
        self.topic = willtop
        self.willmsg = willmsg
        self.clean = clean_fl
        self.keep_alive = keep_alive+3
        self.timer = threading.Timer(self.keep_alive, self.resuscitare)
        self.timer.start()
        self.recvQoS1 = 0

    def afisare(self):
        print(self.conn)
        print(self.addr)
        print(self.client_id)
        print(self.user_name)

    def resuscitare(self):
        timer = threading.Timer(self.will_delay, self.halfCon)
        timer.start()

    def halfCon(self):
        self.conn.close()

    def retrigger(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.keep_alive, self.halfCon)
        self.timer.start()

    def sub(self, topic):
        self.topics.append(topic)

    def unsub(self, topic_name):
        for topic in self.topics:
            if Topic.getTopic(topic) == topic_name:
                self.topics.remove(topic)

    def printTopics(self):
        for topic in self.topics:
            Topic.printTopic(topic)

    def checkTopic(self,topic_name):
        for topic in self.topics:
            if Topic.getTopic(topic) == topic_name:
                return True

    def getConn(self):
        return self.conn

    def getTopic(self):
        return self.topic

    def getMessage(self):
        return self.willmsg

    def getQoS(self):
        return self.QoS

    def getWillDelay(self):
        return self.will_delay

    def getClientID(self):
        return self.client_id

    def setQoS(self, value):
        self.recvQoS1 = value

    def getQos(self):
        return self.recvQoS1

