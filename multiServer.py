import socket
import threading
import atexit

class Room:
    def __init__(self, name, server):
        self.name = name
        self.server = server
        self.connected_clients = []

    # Adiciona cliente na sala
    def add_client(self, client):
        self.connected_clients.append(client)

        msg = f"MESSAGE;Server|Client `{client.name}` has joined the room `{self.name}`"
        self.notify_all(msg, exclude=client)
    
    # Remove cliente da sala e notifica todos os outros que estão na sala
    def remove_client(self, client):
        if client in self.connected_clients:
            self.connected_clients.remove(client)
            msg = f"MESSAGE;Server|Client `{client.name}` has left the room `{self.name}`"
            self.notify_all(msg)

    # Notifica todos os clientes da sala sobre algum evento
    def notify_all(self, data, exclude=None):
        client: Client
        for client in self.connected_clients:
            if client == exclude:
                continue
            client.send_to_client(data)


class Client:
    def __init__(self, connection, address, name, server, room: Room):
        self.connection = connection
        self.address = address
        self.name = name

        self.server: Server = server  
        self.current_room: Room = room

        # Ao criar um cliente, ele é adicionado a uma sala waiting room
        room.add_client(self)

        # Variável usada para interromper um thread
        self.is_connected = True

        # Cria thread para receber dados do cliente
        threading.Thread(target=self.receive_from_client).start()
    
    def send_to_client(self, data):
        try:
            self.connection.send(data.encode('UTF-8'))
        except [BrokenPipeError, OSError] as exc:
            self.is_connected = False
            self.connection.close()
            self.server.remove_client(self)
            self.current_room.remove_client(self)
    
    # Enquanto o client estiver conectado, ele recebe dados
    def receive_from_client(self):
        while self.is_connected:
            data = self.connection.recv(1024).decode('UTF-8')
            self.parse_data(data)
        
    # Dentro da thread que está escutando dados do cliente, trata os dados recebidos
    def parse_data(self, data):
        data = data.split(';')
        command = data[0]

        if command == 'MESSAGE':
            content = data[1]

            package = f'MESSAGE;{self.name}|{content}'
            self.current_room.notify_all(package, exclude=self)

        elif command == 'JOIN_ROOM':
            room_name = data[1]
            self.join_room(room_name)
        
        elif command == 'QUIT_ROOM':
            room_name = 'waiting room'
            self.join_room(room_name)
        
        elif command == 'CHANGE_NAME':
            old_name = self.name
            self.name = data[1]
            msg = f'MESSAGE;Server|User {old_name} changed his name to {self.name}'
            self.current_room.notify_all(msg, exclude=self)
        
        elif command in ['DISCONNECT', '']:
            if self.is_connected:
                self.is_connected = False
                self.connection.close()
                
                self.current_room.remove_client(self)
                self.server.remove_client(self)
    
    # Método usado para mudar de sala
    def join_room(self, room_name):
        if room_name == self.current_room.name:
            return
        room = self.server.get_room(room_name)
        self.current_room.remove_client(self)
        self.current_room = room
        room.add_client(self)

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
        self.server_port = 5000


    def start(self):
        print(f"Starting server at port {self.server_port}")
        self.server_socket.bind(('', self.server_port))
        self.server_socket.listen(self.max_server_clients)
        
        self.accept_clients_connections()
    
    def get_room(self, room_name):
        if room_name not in self.rooms:
            room = Room(room_name, self)
            self.rooms[room_name] = room
        return self.rooms[room_name]

    # Thread que aceita as conexões dos clientes
    def accept_clients_connections(self):

        while True:
            conn, addr = self.server_socket.accept()
            
            if self.max_server_clients == len(self.connected_clients):
                conn.send("ERROR;Server is full".encode())
                conn.close()
                continue
            
            print(f"[LOG] - New client connected from {addr}")

            default_room = self.get_room('waiting room')
            client_name = f'Client-{len(self.connected_clients)}'
            new_client = Client(conn, addr, client_name, self, default_room)

            self.connected_clients.append(new_client)
            new_client.send_to_client(f"CONNECTED;{client_name}")

    
    # Remove cliente da lista de conectados do servidor
    def remove_client(self, client: Client):
        if client in self.connected_clients:
            self.connected_clients.remove(client)
            print(f"[LOG] - Client {client.name} disconnected")
    
    # Encerra o servidor
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
    max_server_clients = get_max_server_clients()
    # max_server_clients = 10
    server = Server(max_server_clients)
    atexit.register(server.close)
    server.start()
