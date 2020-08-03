import uuid
import json
import socket


class Player:

    def __init__(self, addr, udp_port):
        """
        Identify a remote player
        """
        self.identifier = str(uuid.uuid4())
        self.addr = addr
        self.udp_addr = (addr[0], int(udp_port))
        self.num = 0
        self.name = None
        self.tcp_conn = None
        self.out_message = [] #MS!!!
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

    def send_udp_old(self, player_identifier, message):
        """
        Send udp packet to player (game logic interaction)
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sock.setblocking(0)
        try:
            #message = json.dumps({player_identifier: message})
            message = json.dumps({player_identifier:str(self.num),
                                  "message":message})
            sock.sendto(message.encode(), self.udp_addr)
            #sock.close()
        except socket.error as e:
            print(e)

    def send_udp(self, player_identifier, message):
        """
        Send tcp packet to player (game logic interaction)
        previously handled by UDP
        """
        message = json.dumps({player_identifier:str(self.num),
                                  "message":message})
        self.tcp_conn.send(message.encode())
        