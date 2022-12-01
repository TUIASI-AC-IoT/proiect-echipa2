
class Client:
    def __init__(self, client_id, user, password, qos, expiry, willtop, willmsg, clean_fl):
        self.client_id = client_id
        self.user_name = user
        self.password = password
        self.expiry = expiry
        self.QoS = qos
        self.topic = willtop
        self.willmsg = willmsg
        self.clean = clean_fl
