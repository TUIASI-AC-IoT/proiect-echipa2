
class Client:
    def __init__(self, conn, addr, client_id, user, password, qos, expiry, willtop, willmsg, clean_fl):
        self.conn = conn
        self.addr = addr
        self.client_id = client_id
        self.user_name = user
        self.password = password
        self.expiry = expiry
        self.QoS = qos
        self.topic = willtop
        self.willmsg = willmsg
        self.clean = clean_fl

    def afisare(self):
        print(self.conn)
        print(self.addr)
        print(self.client_id)
        print(self.user_name)
