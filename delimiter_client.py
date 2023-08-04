import socket 
from time import sleep

from config import *


def send_messages_with_delimiter(sock, interval, delim):
    msg_templ = 'Message {} from client.'
    n_sending = 5
    
    print('=' * 20)
    sock.send(f'Sending interval = {interval}s'.encode() + delim)
    sleep(1)
    for i in range(n_sending):
        msg = msg_templ.format(i)
        sock.send(msg.encode() + delim)
        print(f'Sent "{msg}"')
        sleep(interval)
    sleep(1)

if __name__ == '__main__':
    sock = socket.socket()
    sock.connect((SERVER_IP, SERVER_PORT))
    sock_remote = sock.getpeername()
    print(f'Connected to remote {sock_remote[0]}:{sock_remote[1]}.')

    sending_intervals = [1, 1e-6, 0]
    for interval in sending_intervals:
        send_messages_with_delimiter(sock, interval, DELIM)
    sock.close()