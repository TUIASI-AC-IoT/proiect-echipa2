import threading

from Client import Client
import struct

UNSUPPORTED_PROTOCOL = bytes('\x20\x02\x00\x84', encoding='utf-8')
CONNACK = bytes('\x20\x09\x00\x00\x06\x22\x00\x0a\x21\x00\x0a', encoding='utf-8')


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

    client_length = hex_to_dec(data[18], data[19])
    for i in range(client_length):
        client_id = client_id + chr(data[20 + i])

    if bit_flag[0] == '1' and bit_flag[5] == '0':
        user_length = hex_to_dec(data[20 + client_length], data[20 + client_length + 1])
        for i in range(user_length):
            user_name = user_name + chr(data[20 + client_length + 2 + i])

        tmp_length = 20 + client_length + 2 + user_length
        pass_length = hex_to_dec(data[tmp_length], data[tmp_length + 1])
        for i in range(pass_length):
            pass_name = pass_name + chr(data[tmp_length + 2 + i])

    if bit_flag[0] == '1' and bit_flag[5] == '1':
        if data[20 + client_length] == 11:
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

    client = Client(conn, addr, client_id, user_name, pass_name, bit_flag[3] + bit_flag[4], None,
                    will_delay, will_topic, will_msg, bit_flag[6], keep_alive)
    conn.send(CONNACK)
    return client


def subscribe(conn, data):
    topic_name = ''
    topic_length = hex_to_dec(data[5], data[6])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[7 + i])
    #print(topic_name)

    sub_opt = data[7 + topic_length]
    bit_sub_opt = bin(sub_opt).replace('0b', '')
    x = bit_sub_opt[::-1]  # this reverses an array.
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


def unsubscribe(conn, data):
    topic_name = ''
    topic_length = hex_to_dec(data[5], data[6])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[7 + i])
    #print(topic_name)

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
    print(topic_length)
    print(topic_name)
    message = ''
    message_length = data[1] - 5 - topic_length
    print(message_length)
    for i in range(message_length):
        message = message + chr(data[7 + topic_length + i])
    print(message)
    identifier = hex_to_dec(data[4+topic_length], data[5+topic_length])

    PUBACK = b'\x40\x02'
    PUBACK += struct.pack('B', data[4 + topic_length])
    PUBACK += struct.pack('B', data[5 + topic_length])
    conn.send(PUBACK)

    for client in clients:
        if Client.checkTopic(client, topic_name):
            clients_receive.append(client)
    return clients_receive


def lastWill(clients, topic_name, message, qos):
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