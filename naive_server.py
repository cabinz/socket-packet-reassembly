import select
import socket
from config import *

sock_recv_buf_size = BIG_RECV_BUF_SIZ # Choose this, packet coalescing can be observed.
# sock_recv_buf_size = SMALL_RECV_BUF_SIZE # Choose this, packet fragmentation can be observed.


if __name__ == '__main__':
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_server.bind((SERVER_IP, SERVER_PORT))
    print(f'Server started at {SERVER_IP}:{SERVER_PORT} with buffer size {sock_recv_buf_size}.')

    sock_server.listen(1)
    sock_conn, client_addr = sock_server.accept()
    print(f'Connected to {client_addr[0]}:{client_addr[1]}.')

    while True:
        r_list, w_list, e_list = select.select([sock_conn], [], [])
        if sock_conn in r_list:
            msg = sock_conn.recv(sock_recv_buf_size)
            if len(msg) > 0:
                print(f'Receive: ', msg)
            else:
                print("Received a null msg, socket has been closed on remote end.")
                sock_conn.close()
                break
