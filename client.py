import socket
import threading
import datetime as dt


class Client:
    def __init__(self, host='localhost', port=5001):
        self.host = host
        self.port = port

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.is_connected = True
        print('Connected to server')
        threading.Thread(target=self.listen_for_messages).start()

        self.start_repl()

    
    def process_commands(self, message: str):
        if message == '/help':
            print('/help - Displays this message')
            print('/quit - Disconnects from the server')
            print('/change_room - Changes the room you are in')
        
        elif message == '/change_room':
            self.change_room()
        
        elif message == '/quit':
            self.disconnect()
    
    def start_repl(self):
        while self.is_connected:
            message = input("> ")

            # Command
            if message and message[0] == '/':
                self.process_commands(message)
            else:
                self.send_message(message)

    def send_message(self, message):
        if self.is_connected:
            self.socket.send(f'MESSAGE;{message}'.encode('UTF-8'))

    def listen_for_messages(self):
        while self.is_connected:
            try:
                message = self.socket.recv(1024).decode('UTF-8')
                self.parse_message(message)
            except Exception as exc:
                pass
        
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
        
        
    def disconnect(self):
        self.close()

    def close(self):
        try:
            self.socket.close()
            self.is_connected = False
        except:
            pass

if __name__ == '__main__':
    Client().connect()
