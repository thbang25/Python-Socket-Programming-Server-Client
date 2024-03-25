# server.py
import socket
import threading
import queue
import os

# Server configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

# Shared data between threads
connected_clients = {}
lock = threading.Lock()

#I want to use UDP socket to manage the chatroom
chatroom_messages = queue.Queue() #Queue to manage messages
chatroom_clients = [] #array of clients in the chatroom

#setup udp connection
server_chat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #
server_chat.bind(("localhost",9100))


#receive messages from cliet
def receive_messageRoom():
    while True:
        try:
        #receive messages
            chatroom_message, addr = server_chat.recvfrom(1024)
            chatroom_messages.put((chatroom_message,addr))
        except Exception as e: #error handling
            pass

#display messages to everyone in the chatroom
def broadcast_to_room():
#while the chatroom still has clients
    while True:
        while not chatroom_messages.empty():
            chatroom_message, addr = chatroom_messages.get()
            print(chatroom_message.decode())
            if addr not in chatroom_clients:
                chatroom_clients.append(addr)
            for client in chatroom_clients:
                try:
                    if chatroom_message.decode().startswith("chatname:"): #if the name starts woth chatname
                        name = chatroom_message.decode()[chatroom_message.decode().index(":")+1:]
                        server_chat.sendto(f"{name} is in the chat!".encode(),client)
                    else:
                        server_chat.sendto(chatroom_message,client)
                        #remove from list of the client is disconnected
                except Exception as e:
                    chatroom_clients.remove(client)

#handle client requests
def handle_client(client_socket, client_address):
    with lock:
        connected_clients[client_address] = client_socket
    
    print(f"[*] {client_address} connected.")
    
    try:
        while True:
            # Receive user option
            option = client_socket.recv(1024).decode()

            if option == "1":
                # Send the list of available clients
                with lock:
                    client_socket.send(str(list(connected_clients.keys())).encode())
            elif option == "5":
                #get the name of the image and start download for client
                client_socket.send(b" 1. Naruto\n 2. Dragon ball\n 3. One Piece\n 4. attack on titan")
                imagename = client_socket.recv(1024).decode()
                
                #try to use server.py as the server
                server_download = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_download.connect(("localhost", 5555))
                
                #read the image data
                image = open(imagename, "rb")
                imagesize = os.path.getsize(imagename)
                
                #the new image name
                server_download.send(("new"+imagename).encode())
                server_download.send(str(imagesize).encode())
                #read the data and send the bytes to client
                imagedata = image.read()
                server_download.sendall(imagedata)
                server_download.send(b"<END>")
                image.close()
                server_download.close()
        
            else:
                # Invalid option
                client_socket.send(b"Invalid option. Please choose again.")
    except Exception as e:
        print(f"Error handling client {client_address}: {str(e)}")

    with lock:
        del connected_clients[client_address]

    print(f"[*] {client_address} disconnected.")
    client_socket.close()


#start our server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)
    print(f"[*] Listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        client, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

        # Send welcome message to client
        client.send(b"Welcome to the server!")

        # Handle client sign-in
        username = client.recv(1024).decode()
        print(f"[*] {addr[0]}:{addr[1]} signed in as {username}")
  
        # Start handling client requests in a separate thread
        client_handler = threading.Thread(target=handle_client, args=(client, addr))
        client_handler.start()
        
t1 = threading.Thread(target=receive_messageRoom) #threads to manage receiving messeges
t2 = threading.Thread(target=broadcast_to_room) #threads to manage brodcasting
#start     
t1.start()
t2.start()

#run program
if __name__ == "__main__":
    print(f"[*] Server running on {SERVER_IP}:{SERVER_PORT}")
    start_server()
