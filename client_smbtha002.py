# client.py
import socket
import threading
import random
import sys


#define server for UDP
#randomize to avoid having the same port when running the code on the same system
client_chat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
client_chat.bind(("localhost",random.randint(8000,9000)))

#facilitate the host and set its perimeters
HostSocket = socket.socket()
HostSocketServer = socket.gethostname()
HostIP = socket.gethostbyname(HostSocketServer)
HostPortNum = 8080

#facilitate the guest and set its perimeters
GuestSocket = socket.socket()
GuestSocketName = socket.gethostname()
GuestIP = socket.gethostbyname(GuestSocketName)
GuestPortNum = 8080


#get the list of available clients on the TCP server option 1
def list_of_clients(c):
    data = c.recv(1024)
    print(f"\nAvailable clients: {data.decode()}")

#create the chatroom where clients can send messages to each other
def chatroom():
    name = input("chatroom Name: ") #your name in the chatroom
    
#receive messages from clients
    def receive():
        while True:
            try:
                chatroom_messages, _ = client_chat.recvfrom(1024)
                print(chatroom_messages.decode())
            except:
                pass
    #initialize
    t = threading.Thread(target=receive) #start thread ti handke each message
    t.start()
    #send message to server
    client_chat.sendto(f"chatname:{name}".encode(), ("localhost",9100))
    
#loop for input and stop when client says exit
    while True:
        chatroom_message = input("")
        if chatroom_message.lower() == "quit":
            exit()
        else:
            client_chat.sendto(f"{name}: {chatroom_message}".encode(), ("localhost",9100))
            
           
#run the program and most of the main arguments
def main_function(server_ipaddress, server_portnum):
    
    #run TCP server connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ipaddress, server_portnum))

    # Receive welcome message from the TCP server
    print(client.recv(1024).decode())

    # Sign in TO the TCP server
    username = input("Enter your username: ")
    client.send(username.encode())
    
    try:
        while True:
            
        # Display menu options
            print("\nOptions:")
            print("1. View available clients")
            print("2. Chat Privately with a peer (you will disconnect from the server)")
            print("3. Reconnect to the server...")
            print("4. Go into chat room with connected clients")
            print("5. Download Available Anime Wallpapers")

        #choose any of the options
            option = input("Enter your choice: ")
            client.send(option.encode()) #sends option to TCP server

            if option == "1":
                #used the server as a way for the user to be able to check if there are people running interface and use the details to connect to them
                list_of_clients(client) #sends the clients currently connected to server
            elif option == "2":
                #choose to be a guest or host by typing the preferred
                choice = input("Choose to be a host or a guest: ")
                
                #if you are the guest on the peer to peer chat
                if choice == "guest":
                    print('This is your IP address: ',HostIP)
                    HostSocketServer = input('Enter peer\'s IP address:')
                    name = input('Enter peer\'s name: ')
                #try to validate the host we are connecting to
                    HostSocket.connect((HostSocketServer, HostPortNum))
 
                    HostSocket.send(name.encode())
                    server_name = HostSocket.recv(1024)
                    server_name = server_name.decode()
                
                    print('connection has been established...')
                    while True:
                        message = (HostSocket.recv(1024)).decode()
                        print(server_name, ":", message)
                        message = input("guest : ")
                        HostSocket.send(message.encode()) 
                        #break out of the loop when guest types exit
                        if message.lower() == "exit":
                            HostSocket.close()
                            break
                
                #if you are the host on the peer to peer chat
                elif choice == "host":
                    GuestSocket.bind((GuestSocketName, GuestPortNum))
                    print( "Binding successful!")
                    print("This is your IP: ", GuestIP)
                    name = input('Enter name: ')
                    GuestSocket.listen(1) 
                    conn, add = GuestSocket.accept()
                #try to validate the guest we are connecting with
                    print("Received connection from ", add[0])
                    print('Connection Established. Connected From: ',add[0])
                    client = (conn.recv(1024)).decode()
                    print('connection has been established...')
                
                    conn.send(name.encode())
                    while True:
                        message = input('host : ')
                        conn.send(message.encode())
                        message = conn.recv(1024)
                        message = message.decode()
                        print('guest: ', message)
                        #break out of the loop when guest types exit
                        if message.lower() == "exit":
                            conn.close()
                            break 
                       
            #used to try to get back to the TCP server when you disconnect to connect to peers or the chatroom          
            elif option == "3":
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect(("127.0.0.1", 9999))

                    print(client.recv(1024).decode())
                    print("reconnecting with new port number..........")

                    username = input("Enter your username: ")
                    client.send(username.encode())
            
            #get in the chatroom
            elif option == "4":
                chatroom()     #chatroom function
             
            #download images using the server   
            elif option == "5":
            #The server will send a list of available wallpapers to choose from
                print("available anime wallpapers...")
                print(client.recv(1024).decode())
                imagename = input("Enter the name of image don't forget the extension(.png) : ")
                client.send(imagename.encode())
                
                if imagename in ["Naruto.png", "Dragon ball.png", "One Piece.png", "attack on titan.png"]:
                    #make the client a receiver
                    client_download = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_download.bind(("localhost",5555))
                    client_download.listen()
                
                    client_var, addressDown = client_download.accept()
                #receive the client name
                    image_name = client_var.recv(1024).decode()
                    print(image_name)
                #get the image size
                    image_size = client_var.recv(1024).decode()
                    print(image_size)
                
                #write the image
                    fileImage = open(image_name, "wb")
                
                    imagebyte = b""
                
                    downloaded = False
                #process all the bytes when complete set to true
                    while not downloaded:
                        data = client_var.recv(1024)
                        if imagebyte[-5:] == b"<END>":
                            downloaded = True
                        
                        else:
                            imagebyte += data
                            
                    fileImage.write(imagebyte)
                    fileImage.close()
                    client_var.close()
                    client_download.close()
                #show the client that we have downloaded
                    print("image downloaded")
                else:
                    print("Invalid image name please try again")
                    
                
                
            else:
            # Invalid option
                print("Invalid option. Please choose again.")
    except ConnectionRefusedError:
        print("Error: Could not connect to the server. Make sure the server is running.")
    finally:
    # Close the client socket
        client.close()
        print("Client disconnected.")


if __name__ == "__main__":
#allow a client to be able to connect to server by entering the desired port number and address
    if len(sys.argv) != 3:
        print("run by typing: python client.py <server_ip> <server_port>")
        sys.exit(1)
#run the functions
    server_ipaddress = sys.argv[1]
    server_portnumber = int(sys.argv[2])
    main_function(server_ipaddress , server_portnumber)
