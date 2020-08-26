import uuid
import json
import socket


class Player:
    
    def __init__(self, addr):
        """
        Identify a remote player
        """
        self.identifier = str(uuid.uuid4())
        self.addr = addr
        self.num = 0
        self.name = None
        self.tcp_conn = None
        self.hand = []

    def send_tcp(self, success, data, sock):
        """
        Send tcp packet to player for server interaction
        """
        success_string = "False"
        if success:
            success_string = "True"
        message = json.dumps({"success": success_string, "message": data})
        sock.send(message.encode())

    def send_msg(self, player_identifier, message):
        """
        Send tcp packet to player (game logic interaction)
        previously handled by UDP
        """
        message = json.dumps({player_identifier:str(self.num),
                                  "message":message})
        self.tcp_conn.send(message.encode())
        