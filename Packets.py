from Client import *

UNSUPPORTED_PROTOCOL = bytes('\x20\x02\x00\x84', encoding='utf-8')
ACCEPTED = bytes('\x20\x02\x00\x00', encoding='utf-8')


def connect(conn, data):
    client_id = ''
    user_name = ''
    pass_name = ''

    protocol_length = data[2] * 10 + data[3]
    protocol_name = ''
    for i in range(protocol_length):
        protocol_name = protocol_name + chr(data[4 + i])
    if protocol_name != 'MQTT':
        conn.send(UNSUPPORTED_PROTOCOL)
        print('Nu MQTT')
    # protocol_version=data[8]%16
    # if protocol_version != 5:
    #    conn.send(UNSUPPORTED_PROTOCOL)
    #    print('NU v5')

    flags = data[9]

    bit_flag = bin(flags).replace('0b', '')
    x = bit_flag[::-1]  # this reverses an array.
    while len(x) < 8:
        x += '0'
    bit_flag = x[::-1]
    print(bit_flag)

    keep_alive = data[10] * 10 + data[11]

    client_length = data[12] * 10 + data[13]
    for i in range(client_length):
        client_id = client_id + chr(data[14 + i])

    if bit_flag[0] == '1':
        user_length = data[14 + client_length] * 10 + data[14 + client_length + 1]
        for i in range(user_length):
            user_name = user_name + chr(data[14 + client_length + 2 + i])

        tmp_length = 14 + client_length + 2 + user_length
        pass_length = data[tmp_length] * 10 + data[tmp_length + 1]
        for i in range(pass_length):
            pass_name = pass_name + chr(data[tmp_length + 2 + i])
    client = Client(client_id, user_name, pass_name, bit_flag[3] + bit_flag[4], None, None, None, bit_flag[6])
    conn.send(ACCEPTED)
