import socket
import threading
import Packets

CONNECT = 16

def Server(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(5)
    print('Asteapta conexiuni (oprire server cu Ctrl‐C)')
    while 1:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            print("Bye bye")
            break
        try:
            threading.Thread(target=comm_thread, args=(conn, addr)).start()
        except:
            print("Eroare la pornirea thread‐ului")


def comm_thread(conn, addr):
    while 1:
        data = conn.recv(1024)
        if data[0] == CONNECT:
            Packets.connect(conn, data)
        if not data:
            break
        print(addr, ' a trimis: ', data)
    conn.close()


if __name__ == '__main__':
    Server('127.0.0.1', 1883)
