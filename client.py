import json
import threading
import socket
import time


class Client:

    def __init__(self,
                 server_host,
                 server_port_tcp=1234,
                 server_port_udp=1234,
                 client_port_udp=1235):
        """
        Create a game server client
        """
        self.identifier = None
        self.server_message = []
        self.room_id = None
        self.client_udp = ("0.0.0.0", client_port_udp)
        self.lock = threading.Lock()
        self.server_listener = SocketThread(self.client_udp,
                                            self,
                                            self.lock)
        self.server_listener.start()
        self.server_udp = (server_host, server_port_udp)
        self.server_tcp = (server_host, server_port_tcp)

        self.name = None

        self.register()

    def create_room(self, name, room_name=None):
        """
        Create a new room on server
        """
        message = json.dumps({"action": "create",
                              #"payload": room_name,
                              "payload": {"room_name": room_name,
                                          "client_name": name},
                              "identifier": self.identifier})

        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        self.room_id = message

    def join_room(self, room_id, name):
        """
        Join an existing room
        """
        self.room_id = room_id
        message = json.dumps({"action": "join",
                              #"payload": room_id,
                              "payload": {"room_id": room_id,
                                          "client_name": name},
                              "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        self.room_id = message

    def autojoin(self):
        """
        Join the first non-full room
        """
        message = json.dumps({"action": "autojoin", "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        self.room_id = message

    def leave_room(self):
        """
        Leave the current room
        """
        message = json.dumps({
            "action": "leave",
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)

    def get_rooms(self):
        """
        Get the list of remote rooms
        """
        message = json.dumps({"action": "get_rooms", "identifier": self.identifier})
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        return message

    def send(self, message, action = "send"):
        """
        Send data to all players in the same room
        """
        message = json.dumps({
            "action": action,
            "payload": {"message": message},
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), self.server_udp)

        #for testing MS!!!
        print("time= ", time.time()) 
        print("sent msg: ", message)

    def sendto(self, recipients, message):
        """
        Send data to one or more player in room
        """
        message = json.dumps({
            "action": "sendto",
            "payload": {
                "recipients": recipients,
                "message": message
            },
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message, self.server_udp)

    def register(self):
        """
        Register the client to server and get a uniq identifier
        """
        message = json.dumps({
            "action": "register",
            #"payload": self.client_udp[1]
            "payload": self.server_listener.port
            #"payload": {"name": self.name,
                        #"port": self.server_listener.port}
        })
        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        self.sock_tcp.close()
        message = self.parse_data(data)
        self.identifier = message

    def parse_data(self, data):
        """
        Parse response from server
        """
        try:
            data = json.loads(data)
            if data['success'] == "True":
                print("Success parsing")
                return data['message']
            else:
                print("Error parsing")
                raise Exception(data['message'])
        except ValueError:
            print(data)


class SocketThread(threading.Thread):
    def __init__(self, addr, client, lock):
        """
        Client udp connection
        """
        threading.Thread.__init__(self)
        self.client = client
        self.lock = lock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.bind(addr)

        self.connection_open = False #used to stop running on exit
        self.port = self.find_port_and_bind(addr)
        print("port= ",self.port)

    def find_port_and_bind(self, addr):
        ip = addr[0]
        port = addr[1]
        while not self.connection_open:
            try:
                self.sock.bind((ip, port))
                self.connection_open = True
                return(port)
            except:
                port += 1

    def run(self):
        """
        Get responses from server
        """
        while self.connection_open:
            data, addr = self.sock.recvfrom(1024)
            self.lock.acquire()
            try:
                self.client.server_message.append(json.loads(data))
            finally:
                self.lock.release()
            #time.sleep(1)
    
    def stop(self):
        """
        Stop thread
        """
        self.connection_open = False
        self.sock.close()

