import socket
import select


def broadcast_data(sock, message):
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock:
            try:
                socket.send(message)
            except:
                # broken socket assume it quit
                socket.close()
                CONNECTION_LIST.remove(socket)


CONNECTION_LIST = []

#
USER_DICT = {}
USER_COUNT = 1

RECV_BUFFER = 4096
PORT = 7012

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(10)

CONNECTION_LIST.append(server_socket)
USER_DICT[server_socket] = "SERVER"

print "[+]Chat server on port %d" % PORT

while 1:
    rlist, wlist, xlist = select.select(CONNECTION_LIST, [], [])
    for sock in rlist:
        if sock == server_socket:
            sockfd, addr = server_socket.accept()
            print "[+]Got connection from %s" % str(addr)

            # recv username
            username = sockfd.recv(512)
            username = username[6:]

            # see if it's already in use
            if username not in USER_DICT.values():
                print "[+]login as %s" % username
                sockfd.send("OK")

                # append the new commer
                CONNECTION_LIST.append(sockfd)
                USER_DICT[sockfd] = username
                USER_COUNT += 1
                print "[+]Current users", USER_DICT.values()
                broadcast_data(sockfd, "%s entered room\n" % str(USER_DICT[sockfd]))
            else:
                sockfd.send("Name already in use")
                print "[-]Asked username already in use"
        else:
            try:
                cmd = sock.recv(RECV_BUFFER)
                if '--status' in cmd:
                    sock.send("Your status is ...\n")
                if '--who' in cmd:
                    msg = "USERS:"+str(USER_DICT.values())+'\n'
                    sock.send(msg)
                if '--broadcast:' in cmd:
                    msg = cmd[12:]
                    broadcast_data(sock, "\r"+"<"+str(USER_DICT[sock])+"> "+msg)

            except:
                broadcast_data(sock, "%s is offlne\n" % str(addr))
                sock.close()
                CONNECTION_LIST.remove(sock)
                usernanme = USER_DICT.pop(sock)
                print "[-]%s is offlne" % username
                print "[+]Current users", USER_DICT.values()
                continue



server_socket.close()
