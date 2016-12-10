import socket
import select

CONNECTION_LIST = []                # List of active socket connection
USER_DICT = {}                      # Dict of socket:username pair

RECV_BUFFER = 4096
PORT = 7023


def broadcast_data(sock, message):
    for s in CONNECTION_LIST:
        if s != server_socket and s != sock:
            try:
                s.send(message)
            except:
                # broken socket assume it quit
                s.close()
                CONNECTION_LIST.remove(socket)


def check_status(sock):
    status = 'Utility will be online soon'
    return status


# Initialize server listening socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(10)

CONNECTION_LIST.append(server_socket)
USER_DICT[server_socket] = "SERVER"

print "[+]Chat server on port %d" % PORT


# Main Message Loop of Server
while 1:
    rlist, wlist, xlist = select.select(CONNECTION_LIST, [], [])
    for sock in rlist:
        # 1 Message from new connection
        if sock == server_socket:
            sockfd, addr = server_socket.accept()
            print "[+]Got connection from %s" % str(addr)

            # recv username
            username = sockfd.recv(512)
            username = username[6:]

            # check if username already in use
            if username not in USER_DICT.values():
                sockfd.send("OK")
                print "[+]login as %s" % username

                # append the new commer
                CONNECTION_LIST.append(sockfd)
                USER_DICT[sockfd] = username
                print "[+]Current users", USER_DICT.values()
            else:
                sockfd.send("Name already in use")
                print "[-]Asked username already in use"
        # 2 Message from users in connection
        else:
            try:
                data = sock.recv(RECV_BUFFER)
                cmd = data [0:5]
                # 1 list who's online
                if 'who' in cmd:
                    sock.send("[*]USER:"+str(USER_DICT.values())+'\n')

                # 2 print current status of user
                elif 'status' in cmd:
                    status = check_status(sock)
                    sock.send("[*]STATUS:%s\n" % status)

                # 3 print Usage menu
                elif 'help' in cmd:
                    sock.send("[*]USAGE:...\n")

                # 4 talk to other user
                elif 'to:' in cmd:
                    pass

                # 5 broadcast to all
                elif 'toall:'in cmd:
                    data = data[6:]
                    broadcast_data(sock, "\r"+"<"+str(USER_DICT[sock])+"> "+data)

                # 6 Undefined command
                else:
                    sock.send("[*]SYS:Undefined command, use help for usage\n")

            except Exception, emsg:
                print "[-]%s" % str(emsg)
                broadcast_data(sock, "[*]USER:%s is offlne\n" % USER_DICT[sock])
                CONNECTION_LIST.remove(sock)
                print "[-]%s is offlne" % USER_DICT[sock]
                usernanme = USER_DICT.pop(sock)
                sock.close()
                print "[+]Current users", USER_DICT.values()
                continue

server_socket.close()





