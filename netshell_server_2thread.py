import socket
import subprocess
import threading
import sys


def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Fail to execute\n"

    return output


def client_handler(client_mirror):

    try:
        while True:
            client_mirror.send("BC.net.sh>>>")
            command = client_mirror.recv(512)
            print "Receive cmd: ", command.rstrip()

            response = run_command(command)
            client_mirror.send(response)

    except:
        client_mirror.close()
        sys.exit()


def command_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 9999))
    server.listen(5)

    while True:
        client, addr = server.accept()

        handler_descriptor = threading.Thread(target=client_handler, args=(client, ))
        handler_descriptor.start()


command_server()
