import socket

def echo_server(port):
    server_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('',port))
    server_socket.listen()

    while 1:
        print ("waiting to accept on a client")
        client_socket, client_addr = server_socket.accept()
        print ("connected to client: %s" %str(client_addr))

        while 1:
            data = client_socket.recv(4096)                 
            print("request received: %s" %str(data))
            if not data: break
            client_socket.sendall(data)

    server_socket.close()

if __name__ == "__main__":
    PORT = 8080
    print ("Running server localhost:%d ..." %PORT)
    echo_server(PORT)
