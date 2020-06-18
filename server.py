#!/usr/bin/python

import argparse
import socket
import json
import time
from threading import Thread, Lock
from rooms import Rooms, RoomNotFound, NotInRoom, RoomFull


def main_loop(tcp_port, udp_port, rooms):
    """
    Start udp and tcp server threads
    """
    lock = Lock()
    udp_server = UdpServer(udp_port, rooms, lock)
    tcp_server = TcpServer(tcp_port, rooms, lock)
    udp_server.start()
    tcp_server.start()
    is_running = True
    print("Simple Game Server.")
    print("--------------------------------------")
    print("list : list rooms")
    print("room #room_id : print room information")
    print("user #user_id : print user information")
    print("quit : quit server")
    print("--------------------------------------")

    while is_running:
        cmd = input("cmd >")
        if cmd == "list":
            print("Rooms :")
            for room_id, room in rooms.rooms.items():
                print("%s - %s (%d/%d)" % (room.identifier,
                                           room.name,
                                           len(room.players),
                                           room.capacity))
        elif cmd.startswith("room "):
            try:
                id = cmd[5:]
                room = rooms.rooms[id]
                print("%s - %s (%d/%d)" % (room.identifier,
                                           room.name,
                                           len(room.players),
                                           room.capacity))
                print("Players :")
                for player in room.players:
                    print(player.identifier, " id = ",
                          player.num, " name= ",
                          player.name )
            except:
                print("Error while getting room informations")
        elif cmd.startswith("user "):
            try:
                player = rooms.players[cmd[5:]]
                print("%s : %s:%d" % (player.identifier,
                                      player.udp_addr[0],
                                      player.udp_addr[1]))
            except:
                print("Error while getting user informations")
        elif cmd == "quit":
            print("Shutting down  server...")
            udp_server.is_listening = False
            tcp_server.is_listening = False
            is_running = False

    udp_server.join()
    tcp_server.join()


class UdpServer(Thread):
    def __init__(self, udp_port, rooms, lock):
        """
        Create a new udp server
        """
        Thread.__init__(self)
        self.rooms = rooms
        self.lock = lock
        self.is_listening = True
        self.udp_port = int(udp_port)
        self.msg = '{"success": %(success)s, "message":"%(message)s"}'
        self.times_got_continue = 0 #Has to belong to room

    def deal(self):
        for room_id, room in rooms.rooms.items():
            if room.time_to_deal:
                room.deal()
                for player in room.players:
                    message = {"hand":str(player.hand).strip('[]')}
                    self.rooms.sendto(player.identifier,
                            room.identifier,
                            player.identifier,
                            message,
                            self.sock)
                    room.time_to_deal = 0
                    time.sleep(0.5)

    def run(self):
        """
        Start udp server
        """
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.udp_port))
        self.sock.setblocking(0)
        self.sock.settimeout(5)
        while self.is_listening:
            self.deal()
            
            try:
                data, address = self.sock.recvfrom(1024)
            except socket.timeout:
                continue

            try:
                data = json.loads(data)
                try:
                    identifier = data['identifier']
                    print("identifier= ",identifier)
                except KeyError:
                    identifier = None

                try:
                    room_id = data['room_id']
                    print("room_id= ",room_id)
                except KeyError:
                    room_id = None

                try:
                    payload = data['payload']
                    print("payload= ",payload)
                except KeyError:
                    payload = None

                try:
                    action = data['action']
                    print("action= ",action)
                except KeyError:
                    action = None

                try:
                    if room_id not in self.rooms.rooms.keys():
                        raise RoomNotFound
                    self.lock.acquire()
                    try:
                        if action == "send":
                            try:
                                self.rooms.send(identifier,
                                                room_id,
                                                payload['message'],
                                                self.sock)
                                time.sleep(0.5)
                            except:
                                pass
                        elif action == "sendto":
                            try:
                                self.rooms.sendto(identifier,
                                                  room_id,
                                                  payload['recipients'],
                                                  payload['message'],
                                                  self.sock)
                                time.sleep(0.5)
                            except:
                                pass
                        elif action == "server":
                            try:
                                #parse
                                if "bidding_winner" in payload["message"].keys():
                                    i = payload["message"]["bidding_winner"]
                                    game_type = payload["message"]["type"]
                                    self.send_prikup(i, game_type, room_id, identifier)
                                    time.sleep(0.5)

                                if "how" in payload["message"].keys():
                                    pasing_num = int(payload["message"]["pasing_num"])
                                    playing_num = int(payload["message"]["playing_num"])
                                    visting_num = int(payload["message"]["visting_num"])
                                    self.send_play_open(room_id, identifier,
                                                        visting_num, pasing_num, 
                                                        playing_num)

                                if "next" in payload["message"].keys():
                                    self.times_got_continue += 1
                                    if self.times_got_continue == 3:
                                        self.rooms.rooms[room_id].time_to_deal = 1
                                        self.times_got_continue = 0

                                if "finalize" in payload["message"].keys():
                                    player_num = int(payload["message"]["player_number"])
                                    self.send_finalize(room_id, identifier, player_num, "request")
                                    self.rooms.rooms[room_id].request_to_finish[player_num] = 1
                                    if sum(self.rooms.rooms[room_id].request_to_finish) == 3:
                                        self.send_finalize(room_id, identifier, player_num, "all")
                            except:
                                pass
                    finally:
                        self.lock.release()
                except RoomNotFound:
                    print("Room not found")

            except KeyError:
                print("Json from %s:%s is not valid" % address)
            except ValueError:
                print("Message from %s:%s is not valid json string" % address)

        self.stop()

    def send_prikup(self, i, game_type, room_id, identifier):
        message = {"prikup":str(self.rooms.rooms[room_id].prikup).strip('[]'),
                   "type":str(game_type)}
        self.rooms.send2all(identifier,
                            room_id,
                            message,
                            self.sock)

    def send_finalize(self, room_id, identifier, player_num, request):
        message = {"finalize":str(request),
                   "player_number":str(player_num)}
        self.rooms.send2all(identifier,
                            room_id,
                            message,
                            self.sock)

    def send_play_open(self, room_id, identifier,
                       visting_num, pasing_num, playing_num):
        for player in self.rooms.rooms[room_id].players:
            if player.num == visting_num:
                visting_id = player.identifier
                visting_hand = player.hand
                print("visthand ",visting_hand)
            elif player.num == pasing_num:
                pasing_id = player.identifier
                pasing_hand = player.hand
                print("pashand ",pasing_hand)
            elif player.num == playing_num:
                playing_id = player.identifier
        message = {"how":"open",
                   "visting_hand":str(visting_hand).strip('[]')}         
        self.rooms.sendto(identifier,
                          room_id,
                          playing_id,
                          message,
                          self.sock)
        time.sleep(0.5)
        self.rooms.sendto(identifier,
                          room_id,
                          pasing_id,
                          message,
                          self.sock)
        time.sleep(0.5)
        message = {"how":"open",
                   "pasing_hand":str(pasing_hand).strip('[]')}         
        self.rooms.sendto(identifier,
                          room_id,
                          playing_id,
                          message,
                          self.sock)
        time.sleep(0.5)
        self.rooms.sendto(identifier,
                          room_id,
                          visting_id,
                          message,
                          self.sock)
        time.sleep(0.5)

    def stop(self):
        """
        Stop server
        """
        self.sock.close()


class TcpServer(Thread):
    def __init__(self, tcp_port, rooms, lock):
        """
        Create a new tcp server
        """
        Thread.__init__(self)
        self.lock = lock
        self.tcp_port = int(tcp_port)
        self.rooms = rooms
        self.is_listening = True
        self.msg = '{"success": "%(success)s", "message":"%(message)s"}'

    def run(self):
        """
        Start tcp server
        """
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', self.tcp_port))
        self.sock.setblocking(0)
        self.sock.settimeout(5)
        time_reference = time.time()
        self.sock.listen(1)

        while self.is_listening:

            #  Clean empty rooms
            if time_reference + 60 < time.time():
                self.rooms.remove_empty()
                time_reference = time.time()
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue

            data = conn.recv(1024)
            try:
                data = json.loads(data)
                action = data['action']
                identifier = None
                try:
                    identifier = data['identifier']
                except KeyError:
                    pass  # Silently pass

                room_id = None
                try:
                    room_id = data['room_id']
                except KeyError:
                    pass  # Silently pass

                payload = None
                try:
                    payload = data['payload']
                except KeyError:
                    pass  # Silently pass
                self.lock.acquire()
                try:
                    self.route(conn,
                               addr,
                               action,
                               payload,
                               identifier,
                               room_id)
                finally:
                    self.lock.release()
            except KeyError:
                print("Json from %s:%s is not valid" % addr)
                conn.send("Json is not valid")
            except ValueError:
                print("Message from %s:%s is not valid json string" % addr)
                conn.send("Message is not a valid json string")

            conn.close()

        self.stop()

    def route(self,
              sock,
              addr,
              action,
              payload,
              identifier=None,
              room_id=None):
        """
        Route received data for processing
        """
        if action == "register":
            client = self.rooms.register(addr, int(payload))
            """
            client = self.rooms.register(addr, 
                                         payload["name"],
                                         int(payload["port"]))
            """
            client.send_tcp(True, client.identifier, sock)
            return 0

        if identifier is not None:
            if identifier not in self.rooms.players.keys():
                print("Unknown identifier %s for %s:%s" % (identifier, addr[0], addr[1]))
                sock.send(self.msg % {"success": "False", "message": "Unknown identifier"})
                return 0

            # Get client object
            client = self.rooms.players[identifier]

            if action == "join":
                try:
                    room_id = payload["room_id"]
                    if room_id not in self.rooms.rooms.keys():
                        raise RoomNotFound()
                    self.rooms.join(identifier,
                                    payload["client_name"],
                                    room_id)
                    client.send_tcp(True, room_id, sock)

                    #Do only once; send players' names and order
                    if self.rooms.rooms[room_id].is_full():
                        for player in self.rooms.rooms[room_id].players:
                            message = {"player_number":str(player.num),
                                       "player_name":player.name}
                            #send to all:
                            self.rooms.send2all(player.identifier,
                                                room_id,
                                                message,
                                                self.sock)
                            time.sleep(0.5)
                            print(player.name, " joined room")
                            self.rooms.rooms[room_id].time_to_deal = 1
                except RoomNotFound:
                    client.send_tcp(False, room_id, sock)
                except RoomFull:
                    client.send_tcp(False, room_id, sock)
            elif action == "autojoin":
                room_id = self.rooms.join(identifier)
                client.send_tcp(True, room_id, sock)
            elif action == "get_rooms":
                rooms = []
                for id_room, room in self.rooms.rooms.items():
                    rooms.append({"id": id_room,
                                  "name": room.name,
                                  "nb_players": len(room.players),
                                  "capacity": room.capacity})
                client.send_tcp(True, rooms, sock)
            elif action == "create":
                room_identifier = self.rooms.create(payload["room_name"])
                self.rooms.join(client.identifier, 
                                payload["client_name"],
                                room_identifier)
                client.send_tcp(True, room_identifier, sock)
            elif action == 'leave':
                try:
                    if room_id not in self.rooms.rooms:
                        raise RoomNotFound()
                    self.rooms.leave(identifier, room_id)
                    client.send_tcp(True, room_id, sock)
                except RoomNotFound:
                    client.send_tcp(False, room_id, sock)
                except NotInRoom:
                    client.send_tcp(False, room_id, sock)
            else:
                sock.send_tcp(self.msg % {"success": "False",
                                          "message": "You must register"})

    def stop(self):
        """
        Stop tcp data
        """
        self.sock.close()


if __name__ == "__main__":
    """
    Start a game server
    """
    parser = argparse.ArgumentParser(description='Simple game server')
    parser.add_argument('--tcpport',
                        dest='tcp_port',
                        help='Listening tcp port',
                        default="1234")
    parser.add_argument('--udpport',
                        dest='udp_port',
                        help='Listening udp port',
                        default="1234")
    parser.add_argument('--capacity',
                        dest='room_capacity',
                        help='Max players per room',
                        default="2")

    args = parser.parse_args()
    rooms = Rooms(int(args.room_capacity))
    main_loop(args.tcp_port, args.udp_port, rooms)
