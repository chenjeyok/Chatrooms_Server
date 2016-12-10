import socket
import select
import sys

if(len(sys.argv) < 2):
    print "Usage: python server.py server_port "
    sys.exit()

PORT = int(sys.argv[1])

CONNECTION_LIST = []                # List of active socket connection
USER_DICT = {}                      # Dict of socket:username pair

RECV_BUFFER = 512

# broadcast message
def Broadcast(sock, message):
    for s in CONNECTION_LIST:
        if s != server_socket and s != sock:
            try:
                s.send(message)
            except Exception, emsg:
                # broken socket
                print "[-]%s" % str(emsg)
                s.close()
                CONNECTION_LIST.remove(socket)
                USER_DICT.pop(socket)


# get socket by user name from {sock, username} pair
def get_sock_by_name(name):
    for sock, username in USER_DICT.items():
        if username == name:
            return sock
    return None


# construct current UserString
def get_UserString():
    UserString = ''
    for username in USER_DICT.values():
        UserString = UserString + username + ' '

    return UserString

# remove a user from CON_LIST & USER_DICT & Broadcast new UserString
def remove_User(sock):
    CONNECTION_LIST.remove(sock)
    print "[-]%s removed" % USER_DICT[sock]
    usernanme = USER_DICT.pop(sock)
    sock.close()
    print "[+]Current users", USER_DICT.values()
    s = get_UserString()
    Broadcast(sock, "[202]%s" % s)

# Initialize server listening socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(10)

CONNECTION_LIST.append(server_socket)
# USER_DICT[server_socket] = "SERVER"

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
            username = username[5:]

            # check if username already in use
            if username not in USER_DICT.values():
                sockfd.send("[201]Login Success")
                print "[+]login as %s" % username

                # append the new commer
                CONNECTION_LIST.append(sockfd)
                USER_DICT[sockfd] = username

                # Broadcast new UserString
                s = get_UserString()
                Broadcast(sock, "[202]%s" % s)
                print "[+]Current users", USER_DICT.values()
            else:
                sockfd.send("[402]Name Already In Use")
                print "[-]Asked username already in use"

        # 2 Message from users in connection
        else:
            try:
                data = sock.recv(RECV_BUFFER)
                cmd = data[0:5]

                # Check if already Login
                if '[300]'in cmd:
                    if username in USER_DICT.values():
                        sock.send("[206]Login repeat")
                    else:
                        pass

                # User List Request
                elif '[350]' in cmd:
                    s = get_UserString()
                    sock.send("[202]"+s)

                # Connection Check Request
                elif '[370]' in cmd:
                    sock.send("[204]Connection alive")

                # Chat Request
                elif '[310]' in cmd:
                    name2 = (data[5:]).rstrip().lstrip()
                    sock2 = get_sock_by_name(name2)
                    name1 = USER_DICT[sock]
                    sock1 = sock
                    if sock2:
                        sock1.send('[203]Chat Confirm')
                        sock2.send('[203]Chat Confirm')
                    else:
                        sock1.send('[405]Peer Offline')

                # Broadcast Request
                elif '[360]'in cmd:
                    data = data[5:]
                    userFrom = '<%s>' % str(USER_DICT[sock])
                    Broadcast(sock, '[205]'+userFrom+data)

                # Undefined command
                else:
                    sock.send("[404]Undefined command, use help for usage\n")

            except Exception, emsg:
                print "[-]%s" % str(emsg)

                CONNECTION_LIST.remove(sock)
                print "[-]%s is offline" % USER_DICT[sock]
                usernanme = USER_DICT.pop(sock)
                sock.close()
                print "[+]Current users", USER_DICT.values()
                s = get_UserString()
                Broadcast(sock, "[202]%s" % s)
                continue

server_socket.close()





