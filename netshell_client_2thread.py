# improved version of netshell client
# Using a thread seperating recv / send

import socket
import threading
import time
import sys


def recv_handler(client_socket):
    # why nested loop?
    # data stream comes in different packets
    # out loop for different data packets
    # inner loop for fragments of one packet
    while True:
        # save cpu resource
        time.sleep(0.1)
        # receiving response
        # last frame < Window Size
        response = ""
        while True:
            buffer = client_socket.recv(4096)
            response += buffer
            if len(buffer) < 4096:
                break
        if len(response):
            print response


def command_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    k = 8001
    client.bind(("127.0.0.1", k))
    client.connect(("127.0.0.1", 9001))

    # spin a recv thread
    recv_thread = threading.Thread(target=recv_handler, args=(client, ))
    recv_thread.start()

    # sender part
    while True:
        # input commmand
        cmd = raw_input()
        print cmd
        client.send(cmd)


command_client()
