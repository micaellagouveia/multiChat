import socket
import threading
import atexit

class Room:
    def __init__(self, name, server):
        self.name = name
        self.server = server
        self.connected_clients = []

    def add_client(self, client):
        """Add a client to the room"""
        self.connected_clients.append(client)
        msg = f"MESSAGE;Server|Client `{client.name}` has joined the room `{self.name}`"
        self.notify_all(msg, exclude=client)
    
    def remove_client(self, client):
        """
        Remove a client from the room and notify all clients in the room
        """
        if client in self.connected_clients:
            self.connected_clients.remove(client)
            msg = f"MESSAGE;Server|Client `{client.name}` has left the room `{self.name}`"
            self.notify_all(msg)

    def notify_all(self, data, exclude=None):
        """Notify all clients in the room of the event"""
        for client in self.connected_clients:
            if client == exclude:
                continue
            client.send_to_client(data)


class Client:
    def __init__(self, connection, address, name, server, room):
        self.connection = connection
        self.address = address
        self.name = name
        self.server = server
        self.current_room: Room = room

        room.add_client(self)

        # Variable used to stop the thread
        self.is_connected = True

        threading.Thread(target=self.receive_from_client).start()
    
    def send_to_client(self, data):
        try:
            self.connection.send(data.encode('UTF-8'))
        except [BrokenPipeError, OSError] as exc:
            self.is_connected = False
            self.connection.close()
            self.server.remove_client(self)
    
    def receive_from_client(self):
        while self.is_connected:
            data = self.connection.recv(1024).decode('UTF-8')
            self.parse_data(data)
        
    def parse_data(self, data):
        data = data.split(';')
        command = data[0]

        if command == 'MESSAGE':
            content = data[1]

            package = f'MESSAGE;{self.name}|{content}'
            self.current_room.notify_all(package, exclude=self)

        elif command == 'JOIN_ROOM':
            self.join_room(data[1])

        elif command == 'LEAVE_ROOM':
            pass
        
        elif command == 'CHANGE_NAME':
            old_name = self.name
            self.name = data[1]

            msg = f'User {old_name} changed his name to {self.name}'
            self.current_room.notify_all(msg)
        
        elif command in ['DISCONNECT', '']:
            if self.is_connected:
                self.is_connected = False
                self.connection.close()
                
                self.current_room.remove_client(self)
                self.server.remove_client(self)





class Server:
    """
    Classe que aceita as conexões e cria um objeto 
    cliente que lida com os dados oriundos da conexão
    """

    def __init__(self, max_server_clients: int):
        self.max_server_clients = max_server_clients
        self.connected_clients = []
        self.rooms = { 'waiting room': Room('waiting room', self) }
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_port = 5001


    def start(self):
        print(f"Starting server at port {self.server_port}")
        self.server_socket.bind(('', self.server_port))
        self.server_socket.listen(self.max_server_clients)
        
        # TODO: Utilizar quando estiver pronto
        # threading.Thread(target=self.accept_clients_connections).start()

        self.accept_clients_connections()
    
    def get_room(self, room_name):
        if room_name not in self.rooms:
            room = Room(room_name, self)
            self.rooms[room_name] = room
        return self.rooms[room_name]

    def accept_clients_connections(self):
        """
        Thread function that accepts clients connections
        """
        while True:
            conn, addr = self.server_socket.accept()
            
            if self.max_server_clients == len(self.connected_clients):
                conn.send("ERROR;Server is full".encode())
                conn.close()
                continue
            
            print(f"New client connected from {addr}")

            default_room = self.get_room('waiting room')
            
            client_name = f'Client-{len(self.connected_clients)}'
            new_client = Client(conn, addr, client_name, self, default_room)

            self.connected_clients.append(new_client)
            new_client.send_to_client(f"CONNECTED;{client_name}")

    def remove_client(self, client):
        if client in self.connected_clients:
            self.connected_clients.remove(client)
            print(f"Client {client.name} disconnected")
        del client
    
    def close(self):
        try:
            self.server_socket.close()
        except:
            pass

def get_max_server_clients():
    while True:
        max_server_clients = input("Enter max number of clients in server: ")

        if max_server_clients.isdigit():
            return int(max_server_clients)
        else:
            print("Please enter a valid number")

if __name__ == "__main__":
    # max_server_clients = get_max_server_clients()
    max_server_clients = 10
    server = Server(max_server_clients)
    atexit.register(server.close)
    server.start()
