import socket
from config import *

sock_buf_size = BIG_RECV_BUF_SIZ # Packet coalescing problem is solved.
# sock_buf_size = SMALL_SOCK_BUF_SIZE # Packet fragmentation problem is solved.

class DelimiterProtocolBuffer:
    """Server and client agree on a delimiter to split messages, 
    preventing packets from coalescing."""
    def __init__(self, sock, delim) -> None:
        self._sock = sock
        self._buf = b''
        self._delim = delim
        
    def get_msg(self):
        """Block until a complete message is recieved.
        
        Returns:
            A bit stream message (without the delimiter). 
            None if the socket is closed.
        """
        while self._delim not in self._buf:
            data_recv = self._sock.recv(sock_buf_size)
            if data_recv == b'': # Socket closed.
                return None
            self._buf += data_recv
        msg, _, self._buf = self._buf.partition(self._delim)    
        return msg


if __name__ == '__main__':
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_server.bind((SERVER_IP, SERVER_PORT))
    sock_server.listen(1)
    print(f'Server started at {SERVER_IP}:{SERVER_PORT}. Buffer size = {sock_buf_size}.')

    sock_conn, client_addr = sock_server.accept()
    print(f'Connected to {client_addr[0]}:{client_addr[1]}.')
    

    delim_buffer = DelimiterProtocolBuffer(sock_conn, DELIM)
    while True:
        msg = delim_buffer.get_msg()
        if msg is not None:
            print(f'Receive: ', msg)
        else:
            print("Socket has been closed on remote end.")
            sock_conn.close()
            break
