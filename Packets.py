import threading

from Client import Client
import struct
import json

UNSUPPORTED_PROTOCOL = bytes('\x20\x02\x00\x84', encoding='utf-8')
CONNACK = bytes('\x20\x09\x00\x00\x06\x22\x00\x0a\x21\x00\x0a', encoding='utf-8')

ID = 1

def hex_to_dec(third_byte, fourth_byte, first_byte=0, second_byte=0):
    no1 = (first_byte // 16) * (16 ** 7)
    no2 = (first_byte % 16) * (16 ** 6)
    no3 = (second_byte // 16) * (16 ** 5)
    no4 = (second_byte % 16) * (16 ** 4)
    no5 = (third_byte // 16) * (16 ** 3)
    no6 = (third_byte % 16) * (16 ** 2)
    no7 = (fourth_byte // 16) * 16
    no8 = (fourth_byte % 16)
    return no1 + no2 + no3 + no4 + no5 + no6 + no7 + no8


def connect(conn, data, addr):
    client_id = ''
    user_name = ''
    pass_name = ''
    will_topic = ''
    will_msg = ''
    will_delay = 0
    clean_start_value = None

    protocol_length = hex_to_dec(data[2], data[3])
    protocol_name = ''
    for i in range(protocol_length):
        protocol_name = protocol_name + chr(data[4 + i])
    if protocol_name != 'MQTT':
        conn.send(UNSUPPORTED_PROTOCOL)
        return 23
    protocol_version = data[8] % 16
    if protocol_version != 5:
        conn.send(UNSUPPORTED_PROTOCOL)
        return 23

    flags = data[9]
    # this will print a in binary.
    bit_flag = bin(flags).replace('0b', '')
    x = bit_flag[::-1]  # this reverses an array.
    while len(x) < 8:
        x += '0'
    bit_flag = x[::-1]
    keep_alive = hex_to_dec(data[10], data[11])

    if bit_flag[6] == '0':
        clean_start_value = hex_to_dec(data[16], data[17], data[14], data[15])


    client_length = hex_to_dec(data[18], data[19])
    for i in range(client_length):
        client_id = client_id + chr(data[20 + i])

    #if bit_flag[0] == '1' and bit_flag[5] == '0':
    #    user_length = hex_to_dec(data[20 + client_length], data[20 + client_length + 1])
    #    for i in range(user_length):
    #        user_name = user_name + chr(data[20 + client_length + 2 + i])

    #    tmp_length = 20 + client_length + 2 + user_length
    #    pass_length = hex_to_dec(data[tmp_length], data[tmp_length + 1])
    #    for i in range(pass_length):
    #        pass_name = pass_name + chr(data[tmp_length + 2 + i])

    if bit_flag[0] == '1' and bit_flag[5] == '1':
        print('aici')
        if data[20 + client_length] == 11:
            print('aici2')
            will_delay = hex_to_dec(data[24 + client_length], data[25+client_length], data[22 + client_length], data[23 + client_length])

            will_topic_length = hex_to_dec(data[32 + client_length], data[33 + client_length])
            for i in range(will_topic_length):
                will_topic = will_topic + chr(data[34 + client_length + i])

            tmp_length = 34 + client_length + will_topic_length
            will_msg_length = hex_to_dec(data[tmp_length], data[tmp_length + 1])
            for i in range(will_msg_length):
                will_msg = will_msg + chr( data [tmp_length + 2 + i])

            tmp_length += will_msg_length + 2
            user_length = hex_to_dec(data[tmp_length], data[tmp_length + 1])
            for i in range(user_length):
                user_name = user_name + chr(data[tmp_length + 2 + i])

            tmp_length += user_length + 2
            pass_length = hex_to_dec(data[tmp_length], data[tmp_length + 1])
            for i in range(pass_length):
                pass_name = pass_name + chr(data[tmp_length + 2 + i])
    else:
        return 23

    if verifUserPass(user_name, pass_name) == 0:
        return 23

    client = Client(conn, addr, client_id, user_name, pass_name, bit_flag[3] + bit_flag[4], clean_start_value,
                    will_delay, will_topic, will_msg, bit_flag[6], keep_alive)

    #if bit_flag[6] == '0':
        #restoreTopics(client)
    if bit_flag[6] == '1':
        expiry_done(client_id)
    conn.send(CONNACK)
    return client

def verifUserPass(user_name, password):
    with open('Autentif.json') as f:
        data = json.load(f)
    for p_id in data:
        p_name = p_id.get('user_name')
        p_pass = p_id.get('password')
        if p_name == user_name and p_pass == password:
            return 1
    return 0


def restoreTopics(client):
    with open('Session.json') as f:
        data = json.load(f)
    for p_id in data:
        p_client_id = p_id.get('client_id')
        if p_client_id == client.getClientID():
            topics = p_id.get('topics')
            for topic in topics:
                client.appendTopics(topic)


def subscribe(conn, data,clients):
    topic_name = ''
    topic_length = hex_to_dec(data[5], data[6])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[7 + i])
    #print(topic_name)

    client_id=''
    for client in clients:
        if client.getConn() == conn:
            client_id = client.getClientID()
    with open('Session.json') as f:
        fisier = json.load(f)

    for f in fisier:
        cl_id = f.get('client_id')
        if cl_id == client_id:
            f.get('topics').append(topic_name.strip('/#'))
            print(f)

    with open("Session.json", "w") as f:
        json.dump(fisier, f, indent=4)

    sub_opt = data[7 + topic_length]
    bit_sub_opt = bin(sub_opt).replace('0b', '')
    x = bit_sub_opt[::-1]
    while len(x) < 8:
        x += '0'
    bit_sub_opt = x[::-1]
    qos = bit_sub_opt[6:]

    SUBACK = b'\x90\x04'
    SUBACK += struct.pack('B', data[2])
    SUBACK += struct.pack('B', data[3])
    SUBACK += b'\x00'
    if qos == '00':
        SUBACK += b'\x00'
    else:
        if qos == '01':
            SUBACK += b'\x01'
        else:
            if qos == '10':
                SUBACK += b'\x02'
            else:
                SUBACK += b'\x80'
    conn.send(SUBACK)
    return topic_name


def unsubscribe(conn, data, clients):
    topic_name = ''
    topic_length = hex_to_dec(data[5], data[6])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[7 + i])


    client_id = ''
    for client in clients:
        if client.getConn() == conn:
            client_id = client.getClientID()

    with open('Session.json') as f:
        fisier = json.load(f)

    for f in fisier:
        cl_id = f.get('client_id')
        if cl_id == client_id:
            f.get('topics').remove(topic_name.strip('/#'))
            print(f)

    with open("Session.json", "w") as f:
        json.dump(fisier, f, indent=4)

    UNSUBACK = b'\xb0\x04'
    UNSUBACK += struct.pack('B', data[2])
    UNSUBACK += struct.pack('B', data[3])
    UNSUBACK += b'\x00'

    UNSUBACK += b'\x00'
    conn.send(UNSUBACK)
    return topic_name


def pingreq(conn):
    conn.send(b'\xd0\x00')


def publishQoS0(clients, data):
    topic_name = ''
    topic_length = hex_to_dec(data[2], data[3])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[4 + i])
    print(topic_length)
    print(topic_name)
    message = ''
    message_length = data[1]-3-topic_length
    print(message_length)
    for i in range(message_length):
        message = message + chr(data[5 + topic_length + i])
    print(message)
    for client in clients:
        if Client.checkTopic(client, topic_name):
            Client.getConn(client).send(data)


def publishQoS1(conn, clients, data):
    clients_receive=[]
    topic_name = ''
    topic_length = hex_to_dec(data[2], data[3])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[4 + i])
    message = ''
    message_length = data[1] - 5 - topic_length
    for i in range(message_length):
        message = message + chr(data[7 + topic_length + i])
    #identifier = hex_to_dec(data[4+topic_length], data[5+topic_length])

    PUBACK = b'\x40\x02'
    PUBACK += struct.pack('B', data[4 + topic_length])
    PUBACK += struct.pack('B', data[5 + topic_length])
    conn.send(PUBACK)

    for client in clients:
        if Client.checkTopic(client, topic_name):
            clients_receive.append(client)
    return clients_receive


def lastWill(clients, topic_name, message, qos):
    global ID
    data = 0
    print(qos)
    if qos == '00':
        data = b'\x30'
        data += struct.pack('B', 3 + len(topic_name) + len(message))
        data += struct.pack('>H', len(topic_name))
        for x in topic_name:
            data += struct.pack('B', ord(x))
        data += struct.pack('B', 0)
        for x in message:
            data += struct.pack('B', ord(x))
        print(data)

        for client in clients:
            if Client.checkTopic(client, topic_name):
                Client.getConn(client).send(data)

    if qos == '01':
        data = b'\x32'
        data += struct.pack('B', 5 + len(topic_name) + len(message))
        data += struct.pack('>H', len(topic_name))
        for x in topic_name:
            data += struct.pack('B', ord(x))
        data += struct.pack('>H', ID)
        ID = ID+1
        data += struct.pack('B', 0)
        for x in message:
            data += struct.pack('B', ord(x))
        for client in clients:
            if Client.checkTopic(client, topic_name):
                Client.setQoS1(client, 1)
                lastWillQoS1(client, data)

    if qos == '10':
        data = b'\x34'
        data += struct.pack('B', 5 + len(topic_name) + len(message))
        data += struct.pack('>H', len(topic_name))
        for x in topic_name:
            data += struct.pack('B', ord(x))
        data += struct.pack('>H', ID)
        ID = ID + 1
        data += struct.pack('B', 0)
        for x in message:
            data += struct.pack('B', ord(x))
        for client in clients:
            if Client.checkTopic(client, topic_name):
                Client.setQoS2(client, 1)
                lastWillQoS2(client, data)

def lastWillQoS1(client, data):
    timer = threading.Timer(5, lastWillQoS1, args=(client, data))
    if Client.getQos1(client):
        try:
            Client.getConn(client).send(data)
        except:
            pass
        timer.start()
    else:
        timer.cancel()


def lastWillQoS2(client, data):
    timer = threading.Timer(5, lastWillQoS2, args=(client, data))
    timer1 = threading.Timer(5, lastWillQoS2, args=(client, data))
    if Client.getQoS2(client) == 1:
        try:
            Client.getConn(client).send(data)
        except:
            pass
        timer.start()
    elif Client.getQoS2(client) == 2:
        timer.cancel()
        print(data)
        pubrel = b'\x62\x03'
        pubrel += struct.pack('B', data[4 + hex_to_dec(data[2], data[3])])
        pubrel += struct.pack('B', data[5 + hex_to_dec(data[2], data[3])])
        print(data[11])
        print(data[12])
        pubrel += b'\x00'
        print(pubrel)
        try:
            Client.getConn(client).send(pubrel)
        except:
            pass
        timer1.start()
    else:
        timer1.cancel()


def publishQoS2(conn, clients, data):
    clients_receive = []
    topic_name = ''
    topic_length = hex_to_dec(data[2], data[3])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[4 + i])
    print(topic_length)
    print(topic_name)
    message = ''
    message_length = data[1] - 5 - topic_length
    print(message_length)
    for i in range(message_length):
        message = message + chr(data[7 + topic_length + i])
    print(message)
    identifier = hex_to_dec(data[4 + topic_length], data[5 + topic_length])

    PUBREC = b'\x50\x02'
    PUBREC += struct.pack('B', data[4 + topic_length])
    PUBREC += struct.pack('B', data[5 + topic_length])
    conn.send(PUBREC)

    for client in clients:
        if Client.checkTopic(client, topic_name):
            clients_receive.append(client)

    return identifier, clients_receive


def pubComp(conn, data):
    PUBCOMP = b'\x70\x02'
    PUBCOMP += struct.pack('B', data[2])
    PUBCOMP += struct.pack('B', data[3])

    conn.send(PUBCOMP)


def expiry(client):
    expiry_time = client.getExpiry()
    if expiry_time is not None and expiry_time < 4294967295:
        client_id = client.getClientID()
        timer = threading.Timer(expiry_time, expiry_done, args=[str(client_id)])
        timer.start()

def expiry_done(client_id):
    with open('Session.json') as f:
        fisier = json.load(f)

    for f in fisier:
        cl_id = f.get('client_id')
        if cl_id == client_id:
            f.get('topics').clear()

    with open("Session.json", "w") as f:
        json.dump(fisier, f, indent=4)



