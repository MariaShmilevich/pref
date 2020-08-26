import json
import threading
import socket
import time


class Client:

    def __init__(self,
                 server_host,
                 server_port_tcp=1234):
        """
        Create a game server client
        """
        self.identifier = None
        self.server_message = []
        self.room_id = None
        self.server_tcp = (server_host, server_port_tcp)

        self.sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_tcp.connect(self.server_tcp)

        self.name = None

        self.register()
        self.lock = threading.Lock()
        self.server_listener = SocketThread(
                                            self,
                                            self.lock,
                                            self.sock_tcp)

    def create_room(self, name, room_name=None):
        """
        Create a new room on server
        """
        message = json.dumps({"action": "create",
                              "payload": {"room_name": room_name,
                                          "client_name": name},
                              "identifier": self.identifier})

        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        
        message = self.parse_data(data)
        self.room_id = message

    def join_room(self, room_id, name):
        """
        Join an existing room
        """
        self.room_id = room_id
        message = json.dumps({"action": "join",
                              "payload": {"room_id": room_id,
                                          "client_name": name},
                              "identifier": self.identifier})
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        
        message = self.parse_data(data)
        self.room_id = message

        self.server_listener.start() #MS!!!

    def leave_room(self):
        """
        Leave the current room
        """
        message = json.dumps({
            "action": "leave",
            "room_id": self.room_id,
            "identifier": self.identifier
        })
        self.sock_tcp.send(message.encode())
        #data = self.sock_tcp.recv(1024)
        #message = self.parse_data(data)
        self.server_listener.stop()

    def get_rooms(self):
        """
        Get the list of remote rooms
        """
        message = json.dumps({"action": "get_rooms", 
                              "identifier": self.identifier})
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
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
        self.sock_tcp.send(message.encode())

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
        self.sock_tcp.send(message.encode())

    def register(self):
        """
        Register the client to server and get a uniq identifier
        """
        message = json.dumps({
            "action": "register",
            "payload": self.server_tcp[1]
        })
        
        self.sock_tcp.send(message.encode())
        data = self.sock_tcp.recv(1024)
        message = self.parse_data(data)
        self.identifier = message

    def setup(self):
        rooms = self.get_rooms()
        print("got room") #MS!!!
        if rooms is not None and len(rooms) != 0:
            for room in rooms:
                print("Room %s (%d/%d)" % (room["name"], 
                    int(room["nb_players"]), int(room["capacity"])))

            # Get first room for tests
            selected_room = rooms[0]['id']
            try:
                self.join_room(selected_room, self.name)
            except Exception as e:
                print("Error : %s" % str(e))
        else:
            self.create_room(self.name, "Pref room")
            print("Client created room  %s" % self.room_id)

    def parse_data_old(self, data):
        """
        Parse response from server
        """
        try:
            print(data)
            data = json.loads(data)
            if data['success'] == "True":
                print("Success parsing")
                return data['message']
            else:
                print("Error parsing")
                
                raise Exception(data['message'])
        except ValueError:
            print(data)

    def parse_data(self, data):
        """
        Parse response from server
        """
        try:
            print(data)
            data = json.loads(data)
            return data['message']
        except ValueError:
            print(data)


class SocketThread(threading.Thread):
    def __init__(self, client, lock, sock):
        """
        Client udp connection
        """
        threading.Thread.__init__(self)
        self.client = client
        self.lock = lock
        self.sock = sock

        self.connection_open = True

    def run(self):
        """
        Get responses from server
        """
        while self.connection_open:
            data, addr = self.sock.recvfrom(1024)
            self.lock.acquire()
            try:
                self.client.server_message.append(json.loads(data))
            except:
                pass
            finally:
                self.lock.release()
            time.sleep(0.1)
    
    def stop(self):
        """
        Stop thread
        """
        self.connection_open = False
        self.sock.close()

