#!/usr/bin/env python3
import socket
from threading import Thread

from config import SERVER_IP, SERVER_PORT, CLIENT_CONNECT_TIMEOUT


class Client(object):
    def __init__(self, server_ip, server_port, client_connect_timeout):
        self._server_ip = server_ip
        self._server_port = server_port
        self._client_connect_timeout = client_connect_timeout
        self._socket = None

    def _create_socket(self):
        self._socket = socket.socket()
        self._socket.settimeout(self._client_connect_timeout)
        self._socket.connect((self._server_ip, self._server_port))
        self._socket.settimeout(None)
        print(f"  >> Client is up @ {self._server_ip}:{self._server_port}")

    def _sender(self):
        while True:
            input_text = input()
            self._socket.send(input_text.encode('utf-8'))

    def _receiver(self):
        while True:
            data = self._socket.recv(1024)
            print(data.decode('utf-8'))

    def start(self):
        self._create_socket()

        self._sender_thread = Thread(target=self._sender)
        self._receiver_thread = Thread(target=self._receiver)

        self._sender_thread.start()
        self._receiver_thread.start()

        self._sender_thread.join()
        self._receiver_thread.join()


def main():
    client = Client(
        server_ip=SERVER_IP,
        server_port=SERVER_PORT,
        client_connect_timeout=CLIENT_CONNECT_TIMEOUT,
    )
    client.start()


if __name__ == '__main__':
    main()
