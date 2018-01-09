import sys
import socket

def client(server_ip, server_port):
    HOST = server_ip
    PORT = server_port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    for line in sys.stdin:
        #print("0")
        s.send(line)
    print "OOPs"
    s.close()

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python client-python.py [Server IP] \
                 [Server Port] < [message]")
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client(server_ip, server_port)


if __name__ == "__main__":
    main()
