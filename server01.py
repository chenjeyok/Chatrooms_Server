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
RECV_BUFFER = 4096
PORT = 7000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(10)

CONNECTION_LIST.append(server_socket)

print "[+]Chat server on port %d" % PORT

while 1:
    rlist, wlist, xlist = select.select(CONNECTION_LIST, [], [])
    for sock in rlist:
        if sock == server_socket:
            sockfd, addr = server_socket.accept()
            CONNECTION_LIST.append(sockfd)
            print "[+]Got connection from %s" % str(addr)
            broadcast_data(sockfd, "%s entered room\n" % str(addr))
        else:
            try:
                data = sock.recv(RECV_BUFFER)
                if data:
                    broadcast_data(sock, "\r"+"<"+str(sock.getpeername())+">"+data)
            except:
                broadcast_data(sock, "%s is offlne\n" % str(addr))
                print "[-]%s is offlne\n" % str(addr)
                sock.close()
                CONNECTION_LIST.remove(sock)
                continue

server_socket.close()





