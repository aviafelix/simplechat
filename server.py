#!/usr/bin/env python3
import socket
from threading import Thread
import time

from config import SERVER_IP, SERVER_PORT, MAX_CONN_COUNT, CONN_ID_INIT


class Server(object):
    def __init__(self, server_ip, server_port, max_conn_count, conn_id_init=0):
        self._server_ip = server_ip
        self._server_port = server_port
        self._max_conn_count = max_conn_count
        self._conn_id_init = conn_id_init
        self._connections, self._threads = {}, {}
        self._socket = None

    def _create_socket(self):
        self._socket = socket.socket()
        self._socket.bind((self._server_ip, self._server_port))
        self._socket.listen(self._max_conn_count)
        print(f"  >> Server is up @ {self._server_ip}:{self._server_port}")

    def _join_threads(self):
        print("The end")
        for _, thread in self._threads.items():
            thread.join()

    def _send_all(self, data, excluded_cid=None):
        for _cid, _conn in self._connections.items():
            if _cid != excluded_cid:
                print(f"({excluded_cid}) said to ({_cid}):", data.decode())
                _conn.send(f'({excluded_cid}) :: '.encode('utf-8') + data)

    def _acceptor(self, cid, conn, connections):
        print(f"  * Thread started: {cid} : {conn}")
        self._send_all(f' [*] Node {cid} is connected'.encode('utf-8'), excluded_cid=None)
        while True:
            try:
                data = conn.recv(1024)
            except Exception as e:
                print(" (!!!) SERVER EXCEPTION: ", e)
                print(f" [*] Node {cid} is disconnected")
                # conn.shutdown()
                conn.close()
                connections.pop(cid)
                self._send_all(
                    f' [*] Node {cid} is disconnected'.encode('utf-8'), excluded_cid=None)
                exit(-1)
            if len(data) == 0:
                print(f"Empty data, node {cid} is disconnected")
                # conn.shutdown()
                conn.close()
                self._connections.pop(cid)
                self._send_all(
                    f' [*] Node {cid} is disconnected'.encode('utf-8'), excluded_cid=None)
                exit(-15)
            self._send_all(data, excluded_cid=cid)

    def start(self):
        self._create_socket()

        cid = self._conn_id_init
        while True:
            try:
                if len(self._connections) >= self._max_conn_count:
                    time.sleep(1.)
                    continue
                conn, addr = self._socket.accept()
                self._connections[cid] = conn
                print(f"  * Client info: {conn} : {addr} (started)")
                thread = Thread(target=self._acceptor, args=(cid, conn, self._connections))
                self._threads[cid] = thread
                thread.start()
                cid += 1
            except Exception as e:
                print('Exception:', e)
                break

        self._join_threads()


def main():
    server = Server(
        server_ip=SERVER_IP,
        server_port=SERVER_PORT,
        max_conn_count=MAX_CONN_COUNT,
        conn_id_init=CONN_ID_INIT,
    )
    server.start()


if __name__ == '__main__':
    main()
