import socket
import select
import threading
import sys
import time
import Queue

# ============ SYS ARG =============

if(len(sys.argv) < 2):
    print "Usage: python server.py server_port "
    sys.exit()

PORT = int(sys.argv[1])

# ==================================


class Server(object):
    def __init__(self):
        self.SOCKS = []                # List of active socket connection
        self.SOCK_NAME = {}            # Dict of login status of users
        self.CreateSocket()
        self.CreateThreads()
        time.sleep(0.1)

    # Initialize server listening socket
    def CreateSocket(self):
        self.SERV_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERV_SOCK.bind(("0.0.0.0", PORT))
        self.SERV_SOCK.listen(10)
        print "[000] Server on port %d" % PORT

    # Create All Threads needed
    def CreateThreads(self):
        # Handle New Connection
        self.T_NewCon = threading.Thread(target=self.NewConnection, args=())
        self.T_NewCon.setDaemon(True)
        self.T_NewCon.start()

        # Sender
        self.T_Sender = threading.Thread(target=self.CreateSender, args=())
        self.T_Sender.setDaemon(True)
        self.T_Sender.start()

        # Receiver
        self.T_Receiv = threading.Thread(target=self.CreateReceiv, args=())
        self.T_Receiv.setDaemon(True)
        self.T_Receiv.start()

    # Thread Accept new connection and append to self.SOCKS List
    def NewConnection(self):
        print '[001] New connection thread start'
        while True:
            sockfd, addr = self.SERV_SOCK.accept()
            self.SOCKS.append(sockfd)
            print "[005] Got connection from %s" % str(addr)

    # Thread Send messages in Message_Send_Queue
    def CreateSender(self):
        print '[002] Sender thread start'
        self.Send_Queue = Queue.Queue()
        while True:
            try:
                if not self.Send_Queue.empty():
                    Fetch = self.Send_Queue.get()
                    Message = Fetch['Message']
                    sock = Fetch['Destination']
                    print '[Snd]' + Message
                    sock.send(Message)
                else:
                    time.sleep(0.1)
            except Exception, emsg:
                print '[430] Sender', str(emsg)
                self.Remove_User_Login(sock)
                self.Broacast_UserList()
                self.Remove_Connection(sock)

        print '[439] Sender down'
        return

    # Thread Receive message from self.SOCKS List and Put to Message_Recv_Queue
    def CreateReceiv(self):
        print '[003] Receive thread start'
        self.Recv_Queue = Queue.Queue()
        while True:
            try:
                rlist, wlist, xlist = select.select(self.SOCKS, [], [], 1)
                for sock in rlist:
                    Message = sock.recv(512)
                    print '[Rcv]' + Message
                    if not Message:
                        # Assume connection broken if recv empty msg
                        raise IOError
                    else:
                        # Put Message into Recv Queue
                        self.Put_to_Recv_Queue(sock, Message)

            except Exception:
                print '[441] Receiver Exception, Removing User'
                self.Remove_User_Login(sock)
                self.Broacast_UserList()
                self.Remove_Connection(sock)

        print '[449] Receiver down'

    # Utility Broadcast message
    def Broadcast(self, message):
        for s in self.SOCKS:
            self.Put_to_Send_Queue(s, message)

    # Utility Construct Message to Send
    def Put_to_Send_Queue(self, sock, message):
        try:
            Pair = {}
            Pair['Destination'] = sock
            Pair['Message'] = message
            self.Send_Queue.put(Pair)
        except Exception, emsg:
            print "[410] Put_to_Send_Queue %s" % str(emsg)

    # Utility Construct Message received
    def Put_to_Recv_Queue(self, sock, message):
        try:
            Pair = {}
            Pair['Source'] = sock
            Pair['Message'] = message
            self.Recv_Queue.put(Pair)
        except Exception, emsg:
            print "[410] Put_to_Recv_Queue %s" % str(emsg)

    # Utility Construct current UserList
    def Get_UserList(self):
        UserList = ''
        for username in self.SOCK_NAME.values():
            UserList = UserList + username + ' '

        return UserList

    # Utility Broadcast current UserList
    def Broacast_UserList(self):
        s = self.Get_UserList()
        self.Broadcast("[202]"+s)

    # Utility Get socket by user name from {sock, username} pair
    def Get_Sock_By_Name(self, name):
        for sock, username in self.SOCK_NAME.items():
            if username == name:
                return sock
        return None

    # Utility Remove a user from SOCK_NAME
    def Remove_User_Login(self, sock):
        if sock in self.SOCK_NAME.keys():
            name = self.SOCK_NAME[sock]
            self.SOCK_NAME.pop(sock)
            print "[102] %s User Removed" % name
        else:
            print "[103] User Not Exist"

    # Utility Remove a connection
    def Remove_Connection(self, sock):
        if sock in self.SOCKS:
            self.SOCKS.remove(sock)
            print "[100] Connection Removed"
        else:
            print "[101] Connection Not Exist"

    # Main Loop, Fetch message From Message_Recv_Queue and Handle them
    def MainLoop(self):
        print '[004] MainLoop Main thread start'
        while True:
            try:
                if not self.Recv_Queue.empty():
                    Fetch = self.Recv_Queue.get()
                    sock = Fetch['Source']
                    Message = Fetch['Message']
                    Header = Message[0:5]

                    # Login Request
                    if '[300]'in Header:
                        username = Message[5:]
                        if username in self.SOCK_NAME.values():
                            self.Put_to_Send_Queue(sock, "[402]Name In Use")
                            print "[104] Asked username already in use"
                        else:
                            # self.SOCKS.append(sockfd)
                            self.SOCK_NAME[sock] = username
                            self.Put_to_Send_Queue(sock, "[201]Login SUCCESS")
                            time.sleep(0.5)  # Avoid 2 Msg Arrive At Same Time
                            self.Broacast_UserList()
                            print "[105] Login as %s" % username
                            print "[106] Users", self.SOCK_NAME.values()

                    # Chat Signals are [31X], From 310 to 315
                    elif '[31' in Header:
                        # Chat Request
                        if '[310]' in Header:
                            Callee = (Message[5:]).rstrip().lstrip()
                            Callee_sock = self.Get_Sock_By_Name(Callee)
                            Caller = self.SOCK_NAME[sock]
                            Caller_sock = sock
                            print '[DB6]', Caller
                            print '[DB7]', Callee
                            if Callee_sock is not None:
                                self.Put_to_Send_Queue(Caller_sock, '[210]Chat Req Sent')
                                self.Put_to_Send_Queue(Callee_sock, '[211]'+Caller)
                            else:
                                self.Put_to_Send_Queue(Caller_sock, '[405]Peer Offline')

                        # Chat Invite Refused
                        elif '[311]' in Header:
                            Caller = (Message[5:]).rstrip().lstrip()
                            Caller_sock = self.Get_Sock_By_Name(Caller)
                            Callee = self.SOCK_NAME[sock]
                            self.Put_to_Send_Queue(Caller_sock, '[212]'+Callee)

                        # Chat Invite Accepted
                        elif '[312]' in Header:
                            Caller = (Message[5:]).rstrip().lstrip()
                            Caller_sock = self.Get_Sock_By_Name(Caller)
                            Callee = self.SOCK_NAME[sock]
                            Callee_sock = sock
                            if Caller_sock is not None:
                                self.Put_to_Send_Queue(Caller_sock, '[213]'+Callee)
                                self.Put_to_Send_Queue(Callee_sock, '[213]'+Caller)

                        # Chat Msg
                        elif '[313]' in Header:
                            Pos = Message.index(':')
                            Content = Message[Pos:]
                            Peer = (Message[5:Pos]).rstrip().lstrip()
                            Peer_sock = self.Get_Sock_By_Name(Peer)
                            From = self.SOCK_NAME[sock]
                            self.Put_to_Send_Queue(Peer_sock, '[214]'+From+Content)

                        # Chat Terminate Request
                        elif '[314]' in Header:
                            Peer = (Message[5:]).rstrip().lstrip()
                            Peer_sock = self.Get_Sock_By_Name(Peer)
                            From = self.SOCK_NAME[sock]
                            self.Put_to_Send_Queue(Peer_sock, '[215]'+From)

                        # Chat File Transmit Request
                        elif '[315]' in Header:
                            pass

                    # User List Query
                    elif '[350]' in Header:
                        s = self.Get_UserList()
                        self.Put_to_Send_Queue(sock, "[202]"+s)

                    # Broadcast Request
                    elif '[360]'in Header:
                        Message = Message[5:]
                        userFrom = '<%s>' % str(self.SOCK_NAME[sock])
                        self.Broadcast('[205]'+userFrom+Message)

                    # Connection Alive Query
                    elif '[370]' in Header:
                        self.Put_to_Send_Queue(sock, "[204]Connection alive")

                    # User Logout
                    elif '[390]' in Header:
                        self.Remove_User_Login(sock)
                        self.Broacast_UserList()

                    # Undefined command
                    else:
                        self.Put_to_Send_Queue(sock, "[404]Undefined command")
                else:
                    time.sleep(0.1)

            except KeyboardInterrupt, emsg:
                print "[-] Main Loop KeyboardInterrupt"
                sys.exit()
            except Exception, emsg:
                print "[-] Main Loop %s" % str(emsg)

# Main()
S1 = Server()
S1.MainLoop()