import sys
import socket

def client(server_ip, server_port):
    HOST = server_ip
    PORT = server_port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    msg = 1
    while msg:
        msg = sys.stdin.readline()
        s.sendall(msg)
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
