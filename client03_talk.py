import socket, select, string, sys


def prompt():
    sys.stdout.write("<me> ")
    sys.stdout.flush()


if(len(sys.argv) < 4):
    print "Usage: python client.py server_ip server_port USERNAME"
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])
username = sys.argv[3]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)

# 1 try to connect to server
try:
    s.connect((host, port))
except:
    print "[-]Unable to connect"
    sys.exit()
print "[+]Connected to server, starting sending message"
prompt()


# 2 send the username and see if already in use
try:
    s.send("LOGIN:"+username)
    result = s.recv(512)
    if "OK" not in result:
        raise
    print "[+]Login as %s" % username
    prompt()
except:
    print "[-]Fail to login as username %s" % username
    sys.exit()


# 3 Main Message Loop
while 1:
    rlist = [sys.stdin, s]
    rlist, wlist, xlist = select.select(rlist, [], [])

    for sock in rlist:
        # 1 Message from local stdin
        if sock != s:
            msg = sys.stdin.readline()
            s.send(msg)
            prompt()

        # 2 Assume connection broken
        else:
            data = sock.recv(512)
            if not data:
                print "[-]Connection from server broken"
                sys.exit()

            # 2.1 Start New Private talk
            elif '[*]TALK' in data:
                pass

            # 2.2 Other server Message
            else:
                sys.stdout.write(data)
                prompt()



























