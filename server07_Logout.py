import socket
import select
import sys
import time

if(len(sys.argv) < 2):
    print "Usage: python server.py server_port "
    sys.exit()

PORT = int(sys.argv[1])
RECV_BUFFER = 512


class Server(object):
    def __init__(self):
        self.SOCKS = []                # List of active socket connection
        self.SOCK_NAME = {}            # Dict of socket:username pair
        self.CreateSocket()

    # Initialize server listening socket
    def CreateSocket(self):
        self.SERV_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERV_SOCK.bind(("0.0.0.0", PORT))
        self.SERV_SOCK.listen(10)
        self.SOCKS.append(self.SERV_SOCK)
        # self.SOCK_NAME[self.SERV_SOCK] = "SERVER"
        print "[+]Chat server on port %d" % PORT

    # Main Loop of Server
    def MainLoop(self):
        while 1:
            rlist, wlist, xlist = select.select(self.SOCKS, [], [])
            for sock in rlist:
                # 1 Message from new connection
                if sock == self.SERV_SOCK:
                    self.NewConnection()
                else:
                    self.MessageHandler(sock)

    # broadcast message
    def Broadcast(self, message):
        for s in self.SOCKS:
            if s != self.SERV_SOCK:
                try:
                    s.send(message)
                except Exception, emsg:
                    # broken socket
                    print "[-]socket remove %s" % str(emsg)
                    self.remove_User(s)
                    s.close()

    # construct current UserString
    def get_UserString(self):
        UserString = ''
        for username in self.SOCK_NAME.values():
            UserString = UserString + username + ' '

        return UserString

    # broadcast current UserString
    def Broacast_UserString(self):
        s = self.get_UserString()
        self.Broadcast("[202]"+s)

    # get socket by user name from {sock, username} pair
    def get_sock_by_name(self, name):
        for sock, username in self.SOCK_NAME.items():
            if username == name:
                return sock
        return None

    # remove a user from CON_LIST & self.SOCK_NAME & Broadcast new UserString
    def remove_User(self, sock):
        self.SOCKS.remove(sock)
        self.SOCK_NAME.pop(sock)
        print "[+]Current users", self.SOCK_NAME.values()

    # Handle new connection
    def NewConnection(self):
            sockfd, addr = self.SERV_SOCK.accept()
            print "[+]Got connection from %s" % str(addr)
            self.SOCKS.append(sockfd)

    # Message from users in connection
    def MessageHandler(self, sock):
        try:
            data = sock.recv(RECV_BUFFER)
            cmd = data[0:5]

            # Check if already Login
            if '[300]'in cmd:
                username = data[5:]
                if username in self.SOCK_NAME.values():
                    sock.send("[402]Name Already In Use")
                    print "[-]Asked username already in use"
                else:
                    # self.SOCKS.append(sockfd)
                    self.SOCK_NAME[sock] = username
                    sock.send("[201]Login SUCCESS")
                    time.sleep(0.1)
                    self.Broacast_UserString()
                    print "[+]login as %s" % username
                    print "[+]Current users", self.SOCK_NAME.values()

            # Chat Request
            elif '[310]' in cmd:
                name2 = (data[5:]).rstrip().lstrip()
                sock2 = self.get_sock_by_name(name2)
                name1 = self.SOCK_NAME[sock]
                sock1 = sock
                if sock2 is not None:
                    sock1.send('[203]Chat Confirm')
                    sock2.send('[203]Chat Confirm')
                else:
                    sock1.send('[405]Peer Offline')

            # User List Request
            elif '[350]' in cmd:
                s = self.get_UserString()
                sock.send("[202]"+s)

            # Broadcast Request
            elif '[360]'in cmd:
                data = data[5:]
                userFrom = '<%s>' % str(self.SOCK_NAME[sock])
                self.Broadcast('[205]'+userFrom+data)

            # Connection Check Request
            elif '[370]' in cmd:
                sock.send("[204]Connection alive")

            # User Logout
            elif '[390]' in cmd:
                self.SOCK_NAME.pop(sock)
                self.Broacast_UserString()

            # Undefined command
            else:
                sock.send("[404]Undefined command, use help for usage\n")

        except Exception, emsg:
            print "[-]socket remove %s" % str(emsg)
            self.remove_User(sock)
            sock.close()

# Main()
S1 = Server()
S1.MainLoop()
