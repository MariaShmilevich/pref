import uuid
from player import Player
from random import shuffle
from random import seed
from datetime import datetime

seed(datetime.now())


class Rooms:

    def __init__(self, capacity=3):
        """
        Handle rooms and set maximum rooms capacity
        """
        self.rooms = {}
        self.players = {}
        self.room_capacity = capacity

    def register(self, addr):
        """
        Register player
        """
        player = None
        for registered_player in self.players.values():
            if registered_player.addr == addr:
                player = registered_player
                break

        if player is None:
            player = Player(addr)
            self.players[player.identifier] = player

        return player

    def join(self, player_identifier, name, room_id=None):
        """
        Add player to room
        """
        if player_identifier not in self.players:
            raise ClientNotRegistered()

        player = self.players[player_identifier]
        player.name = name

        if room_id is None:
            room_id = self.create()

        if room_id in self.rooms:
            if not self.rooms[room_id].is_full():
                i = len(self.rooms[room_id].players)
                self.rooms[room_id].players.append(player)
                self.rooms[room_id].players[i].num = i
                return room_id
            else:
                raise RoomFull()
        else:
            raise RoomNotFound()

    def leave(self, player_identifier, room_id):
        """
        Remove a player from a room
        """
        if player_identifier not in self.players:
            raise ClientNotRegistered()

        player = self.players[player_identifier]

        if room_id in self.rooms:
            self.rooms[room_id].leave(player)
        else:
            raise RoomNotFound()

    def create(self, room_name=None):
        """
        Create a new room
        """
        identifier = str(uuid.uuid4())
        self.rooms[identifier] = Room(identifier,
                                      self.room_capacity,
                                      room_name)
        return identifier

    def remove_empty(self):
        """
        Delete empty rooms one at a time
        """
        room_id_to_delete = None

        for room_id in self.rooms.keys():
            if self.rooms[room_id].is_empty():
                room_id_to_delete = room_id
                break
        if room_id_to_delete:
            del self.rooms[room_id_to_delete]

    def send(self, identifier, room_id, message):
        """
        Send data to all players in room, except sender
        """
        if room_id not in self.rooms:
            raise RoomNotFound()

        room = self.rooms[room_id]
        if not room.is_in_room(identifier):
            raise NotInRoom()

        for player in room.players:
            print("player name ",player.name)
            
            if player.identifier != identifier:
                player.send_msg(identifier, message)

    def send2all(self, identifier, room_id, message):
        """
        Send data to all players in room, including sender
        """
        if room_id not in self.rooms:
            raise RoomNotFound()

        room = self.rooms[room_id]
        if not room.is_in_room(identifier):
            raise NotInRoom()

        for player in room.players:
            player.send_msg(identifier, message)

    def sendto(self, identifier, room_id, recipients, message):
        """
        Send data to specific player(s)
        """
        if room_id not in self.rooms:
            raise RoomNotFound()

        room = self.rooms[room_id]
        if not room.is_in_room(identifier):
            raise NotInRoom()

        if isinstance(recipients, str):
            recipients = [recipients]

        for player in room.players:
            if player.identifier in recipients:
                player.send_msg(identifier, message)


class Room:

    def __init__(self, identifier, capacity, room_name):
        """
        Create a new room on server
        """
        self.capacity = capacity
        self.players = []
        self.identifier = identifier
        if room_name is not None:
            self.name = room_name
        else:
            self.name = self.identifier
        self.deck = list(range(32))
        self.prikup = []
        self.time_to_deal = 0
        self.times_got_continue = [0,0,0]
        self.request_to_finish = [0,0,0]
        self.message_queue = []

    def join(self, player):
        """
        Add player to room. This is never called MS!!!
        """
        if not self.is_full():
            self.players.append(player)
        else:
            raise RoomFull()

    def leave(self, player):
        """
        Remove player from room
        """
        if player in self.players:
            self.players.remove(player)
        else:
            raise NotInRoom()

    def is_empty(self):
        """
        Check if room is empty or not
        """
        if len(self.players) == 0:
            return True
        else:
            return False

    def is_full(self):
        """
        Check if room is full or not
        """
        if len(self.players) == self.capacity:
            return True
        else:
            return False

    def is_in_room(self, player_identifier):
        """
        Check if player is in room
        """
        in_room = False
        for player in self.players:
            if player.identifier == player_identifier:
                in_room = True
                break
        return in_room

    def deal(self):
        if self.time_to_deal:
            shuffle(self.deck)
            for i in [0,1,2]:
                self.players[i].hand = self.deck[i*10:i*10+10]
            self.prikup = self.deck[30:32]
            self.time_to_deal = 0

class RoomFull(Exception):
    pass


class RoomNotFound(Exception):
    pass


class NotInRoom(Exception):
    pass


class ClientNotRegistered(Exception):
    pass
