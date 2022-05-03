import socket
import threading
import datetime as dt
from time import sleep


class Client:
    def __init__(self, host='localhost', port=5001):
        self.host = host
        self.port = port

    def connect(self):
        # Conectando com o socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.is_connected = True

        # Iniciando thread para receber mensagens
        threading.Thread(target=self.listen_for_messages).start()

        self.print_help()
        self.start_repl()
    
    # Recebe mensagens do servidor
    def listen_for_messages(self):
        while self.is_connected:
            try:
                message = self.socket.recv(1024).decode('UTF-8')
                self.parse_message(message)
            except Exception as exc:
                pass

    # Dentro da thread que está escutando mensagens, trata a mensagem recebida pelo server
    def parse_message(self, data):
        data = data.split(';')
        command = data[0]
        content = data[1]

        if command == 'CONNECTED':
            print('Connected to server')
        
        elif command == 'MESSAGE':
            data = content.split('|')
            message_owner, message_content = data[0], data[1]

            current_time = dt.datetime.now().strftime('%H:%M:%S')
            print(f'\n[{current_time}] {message_owner}: {message_content}')  

    # Inicia o REPL
    def start_repl(self):
        sleep(1)
        while self.is_connected:
            message = input("\n> ")

            # Command
            if message and message[0] == '/':
                self.process_commands(message)
            else:
                self.socket.send(f'MESSAGE;{message}'.encode('UTF-8'))
    
    # Processa os comandos recebidos e manda para o servidor usando o protocolo criado
    def process_commands(self, message: str):
        if message[:5] == '/help':
            self.print_help()
   
        elif message[:12] == '/change_room':
            room_name = message.replace('/change_room ', '')
            self.socket.send(f'JOIN_ROOM;{room_name}'.encode('UTF-8'))

        elif message[:12] == '/change_name':
            new_name = message.replace('/change_name ', '')
            self.socket.send(f'CHANGE_NAME;{new_name}'.encode('UTF-8'))

        elif message[:5] == '/quit':
            self.socket.send('DISCONNECT;'.encode('UTF-8'))
            self.close()
        

    # Fecha a conexão
    def close(self):
        try:
            self.socket.close()
            self.is_connected = False
        except:
            pass
    
    # Printa a lista de comandos
    def print_help(self):
        msg = (
            '\n'
            '/help - Displays this message\n'
            '/quit - Disconnects from the server\n'
            '/change_room - Changes the room you are in\n'
            '/change_name - Changes your name\n'
        )
        print(msg)

if __name__ == '__main__':
    Client().connect()
