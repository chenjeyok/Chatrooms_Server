import socket, select, string, sys


def prompt():
    sys.stdout.write("<You>")
    sys.stdout.flush()


if(len(sys.argv) < 3):
    print "Usage: python client.py server_ip server_port"
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)

try:
    s.connect((host, port))
except:
    print "[-]Unable to connect"
    sys.exit()

print "[+]Connected to server, starting sending message"
prompt()

while 1:
    rlist = [sys.stdin, s]
    rlist, wlist, xlist = select.select(rlist, [], [])

    for sock in rlist:
        if sock == s:
            data = sock.recv(4096)
            if not data:
                print "[-]Connection from server broken"
                sys.exit()

            else:
                sys.stdout.write(data)
                prompt()
        else:
            msg = sys.stdin.readline()
            s.send(msg)
            prompt()

