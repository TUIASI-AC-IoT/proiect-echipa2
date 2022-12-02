from Client import *
import struct

UNSUPPORTED_PROTOCOL = bytes('\x20\x02\x00\x84', encoding='utf-8')
CONNACK = bytes('\x20\x09\x00\x00\x06\x22\x00\x0a\x21\x00\x0a', encoding='utf-8')


def hex_to_dec(first_byte, second_byte):
    no1 = (first_byte // 16) * (16 ** 3)
    no2 = (first_byte % 16) * (16 ** 2)
    no3 = (second_byte // 16) * 16
    no4 = (second_byte % 16)
    return no1 + no2 + no3 + no4


def connect(conn, data, addr):
    client_id = ''
    user_name = ''
    pass_name = ''

    protocol_length = data[2] * 10 + data[3]
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
    if bit_flag[0] == '1':
        user_length = data[20 + client_length] * 10 + data[20 + client_length + 1]
        for i in range(user_length):
            user_name = user_name + chr(data[20 + client_length + 2 + i])

        tmp_length = 20 + client_length + 2 + user_length
        pass_length = data[tmp_length] * 10 + data[tmp_length + 1]
        for i in range(pass_length):
            pass_name = pass_name + chr(data[tmp_length + 2 + i])
    client = Client(conn, addr, client_id, user_name, pass_name, bit_flag[3] + bit_flag[4], None, None, None, bit_flag[6])
    conn.send(CONNACK)
    return client


def subscribe(conn, data):
    topic_name = ''
    topic_length = hex_to_dec(data[5], data[6])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[7 + i])
    print(topic_name)

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


def unsubscribe(conn, data):
    topic_name = ''
    topic_length = hex_to_dec(data[5], data[6])
    for i in range(topic_length):
        topic_name = topic_name + chr(data[7 + i])
    print(topic_name)

    UNSUBACK = b'\xb0\x04'
    UNSUBACK += struct.pack('B', data[2])
    UNSUBACK += struct.pack('B', data[3])
    UNSUBACK += b'\x00'

    UNSUBACK += b'\x00'
    print(UNSUBACK)
    conn.send(UNSUBACK)
