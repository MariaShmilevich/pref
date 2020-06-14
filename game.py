"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.starting_template
"""
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "ПРЕФЕРАНС"
CARD_SCALING_FACTOR = .11
#SF = CARD_SCALING_FACTOR 

from card import *
from bidding import *
from pool import *
from client import *

from datetime import datetime
from random import seed
from random import randint
from random import shuffle
#seed(1)
seed(datetime.now())

class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.theme = arcade.Theme()

        self.client = Client("127.0.0.1", 1234, 1234, 1235)
        self.players = ["Dummy", "Dummy", "Dummy"]
        """
        The first hand at the beginning will be the first 
        person connected to the server - player number 0
        """
        self.turn = 0  

        self.my_num = 0 #my order number in the players' list 
        self.my_shift = 0 #used to to figure out drawing position

        self.score = Score(20)

        """
        #For pool writing:
        # Пуля: Юг, Север, Восток
        self.pool = [0,0,0]
        # Гора: Юг, Север, Восток
        self.hill = [20,20,20]
        # Висты: юг на север и т.д.
        #[[S/N,S/E],[N/S,N/E],[E/S,E/N]
        self.vist_counts = [[0,0],[0,0],[0,0]]
        """

        self.hand = []
        self.deck = []
        self.prikup = []
        self.north_hand = []
        self.east_hand = []

        self.connecting_stage = 1 #connecting to server
        self.waiting_stage = 0

        self.init_round()
        
        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None

        self.south_list = None
        self.north_list = None
        self.east_list = None
        self.prikup_list = None
        self.current_trick_list = None
        self.collected_tricks_list = None

        self.button_list = None
        self.shape_list = None
        
        self.set_deck()

    def init_round(self):
        self.bidding_turn = self.turn
        self.current_turn = self.turn #trick winner
        self.visting_turn = 0
        self.bidding_index = 0
        self.curr_bid_winner = -2

        self.bids=[0,0,0] #becomes for instance ["6s", "pas", "pas"]
        self.vists=["","",""] 
        self.current_trick = [0,0,0,"n"] #last one is cur. trick's suit
        self.current_round_type = 0 #"reg","miser" or "raspas"
        self.current_round = {"trump":"n",
                              "value":0,
                              "type":"reg",#or "miser" or "raspas"
                              "status":"open"} 
        self.num_of_tricks = [0,0,0]
        self.current_offer = {"value":0,
                              "offering_hand":0,
                              "accepting_hand":0}
        self.offered_to_end_round = 0

        #stages
        self.waiting_stage = 0
        self.bidding_stage = 0
        self.prikup_stage = 0
        self.order_stage = 0
        self.vist_stage = 0
        self.choosing_stage = 0 
        self.new_round_stage = 0
        self.playing_stage = 0
        self.writing_stage = 0 #MS!!!
        self.show_stage = 0

        self.times_prikup_opened = 0
        self.times_prikup_collected = 0
        self.times_prikup_discarded = 0
        self.times_vist_sent = 0
        self.vist_complete = 0

    def set_deck(self):
        for i in range(32):
            new_card=Card(picz[i][0], picz[i][1], picz[i][2],
                      arcade.Sprite(picz[i][3],SF))
            self.deck.append(new_card)

    def parse_server_msg(self):
        """ 
        Parse UDP message from server
        """
        message = self.client.server_message

        if not "message" in message.keys():
            return
        print("received msg: ", message)
        self.client.got_udp_msg = 0
        #Done at the beginning: setup players' order & names
        if "player_name" in message["message"].keys():
            i = int(message["message"]["player_number"])
            self.players[i] = message["message"]["player_name"]
            if self.client.identifier in message.keys():
                self.my_num = i
                self.set_shift()
            if i == 2:
                self.waiting_stage = 0
        #Server dealt next round
        if "hand" in message["message"].keys():
            self.clear_sprite_lists()
            card_num_list = list(map(int, 
                        message["message"]["hand"].split(',')))
            print("My hand: ", card_num_list)
            deal_open(self.hand, card_num_list, self.deck)
            self.deal_new_round()
            self.waiting_stage = 0
            #self.bidding_stage = 1
        #Client sent bid
        if "bid" in message["message"].keys():
            i = int(message["message"]["player_number"])
            self.bids[i] = message["message"]["bid"]
            self.bidding_turn = int(message["message"]["bidding_turn"])
            self.bidding_index = int(message["message"]["bidding_index"])

        #Server sent prikup after bidding is done 
        if "prikup" in message["message"].keys():
            card_num_list = list(map(int, 
                        message["message"]["prikup"].split(',')))
            print("Prikup: ", card_num_list)
            game_type = message["message"]["type"]
            deal_open(self.prikup, card_num_list, self.deck, "no_sort")
            self.move_to_prikup_stage(game_type)

        #Bidding winner collected prikup
        if "collected_prikup" in message["message"].keys():
            num = int(message["message"]["player_number"])
            i = int(message["message"]["collected_prikup"])
            
            if i == 2: #collected both cards
                if self.current_round_type != "miser_bp":
                    self.remove_prikup(num, "show")
                else:
                    self.remove_prikup(num, "miser_bp")
                    self.move_to_order_stage()

        #Bidding winner discarded prikup
        if "discarded_prikup" in message["message"].keys():
            num = int(message["message"]["player_number"])
            i = int(message["message"]["discarded_prikup"])
            
            if i == 2: #discarded both cards
                self.remove_prikup(num, "hide")
                self.move_to_order_stage()

        #Bidding winner ordered game round
        if "playing" in message["message"].keys():
            num = int(message["message"]["player_number"])
            order = message["message"]["playing"]
            index = int(message["message"]["index"])
            self.move_to_vist_stage(order, index)

        #Player sent vist/pas
        if "vist" in message["message"].keys():
            num = int(message["message"]["player_number"])
            vist = message["message"]["vist"]
            self.vists[num] = vist
            self.visting_turn = int(message["message"]["visting_turn"])
            self.times_vist_sent = int(message["message"]["times_vist_sent"])
            self.vist_complete = int(message["message"]["vist_complete"])

        #Player/server sent open/closed
        if "how" in message["message"].keys():
            self.playing_stage = 1
            self.choosing_stage = 0
            how = message["message"]["how"]
            if how == "closed":
                self.current_round["status"]="closed"
            else: #open
                self.current_round["status"]="open"
                if "visting_hand" in message["message"].keys():
                    vist_num_list = list(map(int, 
                        message["message"]["visting_hand"].split(',')))
                    print("visting_hand: ", vist_num_list)
                    index = self.vists.index("вист")
                    print(vist_num_list)
                    self.setup_open_hand(vist_num_list, index)
                if "pasing_hand" in message["message"].keys():
                    pas_num_list = list(map(int, 
                        message["message"]["pasing_hand"].split(',')))
                    print("pasing_hand: ", pas_num_list)
                    index = self.vists.index("пас")
                    print(pas_num_list)
                    self.setup_open_hand(pas_num_list, index)

        #Player sent card put on table
        if "card_num" in message["message"].keys():
            num = int(message["message"]["player_number"])
            i = int(message["message"]["card_num"])
            j = int(message["message"]["sprite_num"])
            self.current_trick[3] = message["message"]["suit"]
            
            card = self.deck[i]
            self.add_card_to_trick(card, j, num)

        #Player sent current trick winner
        if "trick_winner" in message["message"].keys():
            num = int(message["message"]["player_number"])
            trick_winner = int(message["message"]["trick_winner"])
            self.remove_trick(trick_winner)

        #Player sent offer to end round
        if "offer" in message["message"].keys():
            num = int(message["message"]["player_number"])
            offer = int(message["message"]["offer"])
            self.setup_current_offer(num, offer)

        #Player sent response to the offer to end round
        if "answer" in message["message"].keys():
            num = int(message["message"]["player_number"])
            answer = str(message["message"]["answer"])
            self.offered_to_end_round = 0
            self.disable_buttons([12,13])
            if answer == "yes":
                self.new_round_stage = 1


    def setup_open_hand(self, card_num_list, index):
        if (index - self.my_num)%3 == 1:
            deal_open(self.north_hand, card_num_list, self.deck)
            for i in range(10):
                self.north_list.pop()
            for i in range(10):
                self.north_list.append(self.north_hand[i].face)
                self.north_hand[i].set_north_coord(i)

        elif (index - self.my_num)%3 == 2:
            deal_open(self.east_hand, card_num_list, self.deck)
            for i in range(10):
                self.east_list.pop()
            for i in range(10):
                self.east_list.append(self.east_hand[i].face)
                self.east_hand[i].set_east_coord(i)

    def set_shift(self):
        if self.my_num == 1:
            self.my_shift = 2
        elif self.my_num == 2:
            self.my_shift = 1
        else:
            self.my_shift = 0 

    def open_prikup(self, i):
        self.prikup_list.pop(i)
        self.prikup_list.insert(i, self.prikup[i].face)
        self.prikup[i].set_prikup_coord(i)
        self.times_prikup_opened += 1

    def collect_prikup(self,x,y):
        if self.times_prikup_opened < 2:
            return
        if self.curr_bid_winner != self.my_num:
            return
        #Click right mouse button
        i = card_chosen(self.prikup,x,y)
        if i < 0:
            return    
        self.prikup_list.pop(i)

        if self.current_round_type != "miser_bp":
            n=len(self.hand) 
            self.hand.append(self.prikup[i])

            self.south_list.append(self.hand[n].face)
            self.hand[n].set_south_coord(n)

            self.hand.sort(reverse=True, key = get_key)

            for j in range(len(self.hand)):
                self.south_list.pop()
            for j in range(len(self.hand)):
                self.south_list.append(self.hand[j].face)
                self.hand[j].set_south_coord(j)

        self.prikup.pop(i)
        self.times_prikup_collected += 1

        message = {"player_number":str(self.my_num),
                   "collected_prikup":str(self.times_prikup_collected)}
        self.client.send(message) 

        if self.current_round_type == "miser_bp" and\
            self.times_prikup_collected == 2:
            self.move_to_order_stage()

    def remove_prikup(self, num, show):
        for i in [0,1]:
            if show == "miser_bp":
                self.prikup_list.pop()
                continue
            if num == (self.my_num + 1)%3:
                if show == "show":
                    self.prikup_list.pop()
                    self.north_list.append(self.prikup[i].face)
                    self.prikup[i].set_north_coord(10+i)
                elif show == "hide":
                    self.north_list.pop()
            elif num == (self.my_num + 2)%3:
                if show == "show":
                    self.prikup_list.pop()
                    self.east_list.append(self.prikup[i].face)
                    self.prikup[i].set_east_coord(10+i)
                elif show == "hide":
                    self.east_list.pop()
            
    def discard_prikup(self,x,y):
        if self.times_prikup_opened < 2:
            return
        #Click left or right mouse button
        if len(self.hand) > 10:
            i = card_chosen(self.hand,x,y) 
            if i > -1:
                self.south_list.pop(i)
                self.hand.pop(i)
                self.times_prikup_discarded += 1
        if self.times_prikup_discarded == 2:

            self.hand.sort(reverse=True, key = get_key)

            for j in range(len(self.hand)):
                self.south_list.pop()
            for j in range(len(self.hand)):
                self.south_list.append(self.hand[j].face)
                self.hand[j].set_south_coord(j)

            message = {"player_number":str(self.my_num),
                       "discarded_prikup":str(self.times_prikup_discarded)}
            self.client.send(message)

            self.move_to_order_stage()

    def move_to_order_stage(self):
        self.times_prikup_opened = 0
        self.times_prikup_collected = 0
        self.times_prikup_discarded = 0
        self.prikup_stage = 0
        
        if self.current_round_type == "reg":
            self.order_stage = 1
        elif self.current_round_type =="miser" or \
            self.current_round_type =="miser_bp":
            self.order_stage = 0
            self.playing_stage = 1
            self.current_round["status"]="open"

            #setup artificial vist/pas to facilitate open cards
            #need to fix this for display
            i = self.curr_bid_winner
            self.vists[i] = "мизер"
            self.vists[(i+1)%3] = "вист"
            self.vists[(i+2)%3] = "пас"
            if self.my_num == (i+1)%3:
                self.send_open() 

    def move_to_prikup_stage(self, game_type):    
        self.bidding_stage = 0
        self.current_round_type = game_type #"reg","miser" or "raspas"
        self.current_round["type"] = game_type
        
        if self.curr_bid_winner >= 0:
            self.prikup_stage = 1
            self.open_prikup(0)
            self.open_prikup(1)      
        else: #raspas
            self.playing_stage = 1
            self.open_prikup(1)
            self.current_trick[3] = self.prikup[1].suit
            self.current_round["status"] = "closed"

    def create_sprite_list(self):
        self.south_list = arcade.SpriteList()
        self.north_list = arcade.SpriteList()
        self.east_list = arcade.SpriteList()
        self.prikup_list = arcade.SpriteList()
        self.current_trick_list = arcade.SpriteList()
        self.collected_tricks_list = arcade.SpriteList()


    def create_button_list(self):
        self.button_list = []
        
        miser_button = RegularButton(70, 150, self.bid_miser, "мизер")
        reg_button = RegularButton(210, 150, self.bid_reg, "6 пик")
        pas_button = RegularButton(350, 150, self.bid_pas, "пас")
        order_button = RegularButton(250, 300, self.send_order, "заказ")
        show_pool_button = ShowPoolButton(710, 12, self.show_pool, "Показать пулю")
        connect_button = ConnectButton(500,400,self.send_name, "Играть")
        vist_button = RegularButton(70, 150, self.send_vist, "вист")
        pas_vist_button = RegularButton(210, 150, self.send_vist_pas, "пас")
        open_button = WideButton(70, 150, self.send_open, "в открытую")
        closed_button = WideButton(250, 150, self.send_closed, "взакрытую")
        continue_button = WideButton(200, 300, self.send_continue, "продолжить")
        offer_button = WideButton(710, 97, self.send_offer, "согласен на")
        yes_button = RegularButton(200, 290, self.send_yes, "да")
        no_button = RegularButton(300, 290, self.send_no, "нет")
        
            
        self.button_list.append(miser_button)      #0
        self.button_list.append(reg_button)        #1
        self.button_list.append(pas_button)        #2
        self.button_list.append(order_button)      #3
        self.button_list.append(show_pool_button)  #4
        self.button_list.append(connect_button)    #5
        self.button_list.append(vist_button)       #6
        self.button_list.append(pas_vist_button)   #7
        self.button_list.append(open_button)       #8
        self.button_list.append(closed_button)     #9
        self.button_list.append(continue_button)   #10
        self.button_list.append(offer_button)      #11
        self.button_list.append(yes_button)        #12
        self.button_list.append(no_button)         #13

    def disable_buttons(self, list_to_disable):
        for i in list_to_disable:
            self.button_list[i].disable()
        #Note that each button is enabled on drawing

    def connect_to_server(self):
        rooms = self.client.get_rooms()
        if rooms is not None and len(rooms) != 0:
            for room in rooms:
                print("Room %s (%d/%d)" % (room["name"], int(room["nb_players"]), int(room["capacity"])))

            # Get first room for tests
            selected_room = rooms[0]['id']
            try:
                self.client.join_room(selected_room, self.client.name)
            except Exception as e:
                print("Error : %s" % str(e))
        else:
            self.client.create_room(self.client.name, "Pref room")
            print("Client created room  %s" % self.client.room_id)
            
    def setup(self):
        #self.connect_to_server()
        # Create your sprites and sprite lists here
        self.create_sprite_list()

        # Create our on-screen GUI buttons
        self.create_button_list()
        
        self.textbox_list.append(arcade.TextBox(70, 300, width=80,\
            theme=arcade.Theme(),font_size=16))
        self.textbox_list.append(arcade.TextBox(200, 400, width=200,\
            theme=arcade.Theme(),font_size=16))
        self.textbox_list.append(arcade.TextBox(680, 56, width=60,\
            theme=arcade.Theme(),font_size=12)) #MS!!! offer
          
        #for drawing the pool
        self.shape_list = make_pool(320,300,600,400)
    
    def clear_sprite_lists(self):
        del self.hand[:]
        del self.prikup[:]
        del self.north_hand[:]
        del self.east_hand[:]
        while len(self.south_list) > 0:
            self.south_list.pop()
        while len(self.north_list) > 0:
            self.north_list.pop()
        while len(self.east_list) > 0:
            self.east_list.pop()
        while len(self.prikup_list) > 0:
            self.prikup_list.pop()
        while len(self.current_trick_list) > 0:
            self.current_trick_list.pop()
        while len(self.collected_tricks_list) > 0:
            self.collected_tricks_list.pop()

    def deal_new_round(self):
        for i in range(10):
            
            self.south_list.append(self.hand[i].face)
            self.hand[i].set_south_coord(i)

            dummy_card = DummyCard()
            self.north_list.append(dummy_card.back)
            dummy_card.set_north_coord(i)

            dummy_card = DummyCard()
            self.east_list.append(dummy_card.back)
            dummy_card.set_east_coord(i)

        for i in [0,1]:
            dummy_card = DummyCard()
            self.prikup_list.append(dummy_card.back)
            dummy_card.set_prikup_coord(i)
            
        self.turn = (self.turn + 1)%3
        self.init_round()
        self.bidding_stage = 1 

    def draw_connect(self):
        temp = "Please type your name in latin alphabet lowercase"
        arcade.draw_text(temp, 200,300, arcade.color.BLACK,font_size=16)
        self.textbox_list[1].draw()
        self.button_list[5].draw()

    def draw_frame(self):
        #South, myself
        arcade.draw_text(self.players[self.my_num],200,1,
                         arcade.color.BLACK)
        arcade.draw_text(self.vists[self.my_num],300,1,
                         arcade.color.BLACK)
        #North
        arcade.draw_text(self.players[(self.my_num+1)%3],200,580,
                         arcade.color.BLACK)
        arcade.draw_text(self.vists[(self.my_num+1)%3],300,580,
                         arcade.color.BLACK)
        #East
        arcade.draw_text(self.players[(self.my_num+2)%3],670,570,
                         arcade.color.BLACK)
        arcade.draw_text(self.vists[(self.my_num+2)%3],750,570,
                         arcade.color.BLACK)

        #Always show "Показать пулю" Button
        self.button_list[4].draw()
        
        self.north_list.draw()
        self.south_list.draw()
        self.east_list.draw()
        self.prikup_list.draw()

    def draw_offer(self):
        self.button_list[11].draw()
        self.textbox_list[2].draw()
        arcade.draw_text("взяток", 727, 48,
                         arcade.color.BLACK,
                         font_size=16)

    def draw_order(self, bids):
        #this shouldn't happen, but just to be safe
        if self.curr_bid_winner < 0:
            return 
          
        temp = "заказать " + str(bids[self.curr_bid_winner]) +\
                " или выше\ntype 6s for 6 пик, 7c for 7 треф,\n" +\
                "8d for 8 бубей, 9h for 9 червей,\n" +\
                "10n for 10 без козыря и т.д."
        #Add -3 bez treh MS!!!
        arcade.draw_text(temp, 40,200, arcade.color.BLACK,font_size=16)
        self.textbox_list[0].draw()
        self.button_list[3].draw()

    def draw_bids(self, bids):
        for i in[0,1,2]: 
                if bids[i] != 0:
                    arcade.draw_text(bids[i],
                        bid_msg_x_coord[(i + self.my_shift)%3],
                        bid_msg_y_coord[(i + self.my_shift)%3],
                        arcade.color.BLACK,
                        font_size=16)

    def draw_slovo(self):
        i = self.bidding_turn
        arcade.draw_text("Слово:",
                         turn_msg_x_coord[(i + self.my_shift)%3], 
                         turn_msg_y_coord[(i + self.my_shift)%3],
                         arcade.color.BLACK,
                         font_size=16)

    def draw_cont_bidding(self,bids):
        i = self.bidding_turn
        if bids[i] == 0 and bids[(i+1)%3] != "мизер"\
	            and bids[(i+2)%3] != "мизер":
            #Draw Miser Button
            self.button_list[0].draw()
            #Draw Regular Game Button
            self.button_list[1].text = bidding_order[self.bidding_index]
            self.button_list[1].draw()
        elif bids[i] == "мизер":
            #User pressed "Miser" before
            #Button should show "Miser bez prikupa"
            self.button_list[0].text = "мизер БП"
            self.button_list[0].draw()
            #Do not draw Regular Game Button
        elif bids[i] == "мизер БП":
            #draw only "пас" Button (below)
            pass
        elif bids[i] != "пас":
            #Draw Regular Game Button
            self.button_list[1].text = bidding_order[self.bidding_index]
            self.button_list[1].draw()
        #always draw Pas Button
        self.button_list[2].draw()

    def draw_visting(self):
        self.button_list[6].draw()

        if self.visting_turn == (self.curr_bid_winner+2)%3 and\
            self.vists[(self.curr_bid_winner+1)%3] == "пас"\
            and (self.current_round["value"] == 6 or self.current_round["value"] == 7):
            self.button_list[7].text = "свой"
        if self.current_round["value"] == 6 and self.current_round["trump"] == "s":
            pass #only vist for 6 spades
        else:
            self.button_list[7].draw()

    def draw_continue(self):
        self.button_list[10].draw()

    def draw_playing(self):
        self.current_trick_list.draw()
        self.collected_tricks_list.draw()
        draw_star_new(star_x_coord[(self.current_turn + self.my_shift)%3],
                      star_y_coord[(self.current_turn + self.my_shift)%3],
                      arcade.color.BARBIE_PINK,
                      arcade.color.BARBIE_PINK)
        if self.current_round["status"] == "open" and \
            self.vists[self.my_num] != "пас" and \
            not self.offered_to_end_round:
            self.draw_offer()
        else:
            self.button_list[11].disable()
        if self.offered_to_end_round:
            self.draw_accepting_offer()
            
        #self.disable_buttons([0,1,2,3,5,6,7,8,9,10]) #MS!!!

    def draw_accepting_offer(self):
        temp = self.players[self.current_offer["offering_hand"]]+ \
            " предлагает согласиться на " + \
            str(self.current_offer["value"]) + " взяток"
                
        arcade.draw_text(temp, 150, 310,
                         arcade.color.BLACK,
                         font_size=16)
        if self.current_offer["accepting_hand"] == self.my_num:
            self.button_list[12].draw()
            self.button_list[13].draw()
        else:
            self.disable_buttons([12,13])

    def draw_writing(self):
        #self.num_of_tricks
        text = "South " + str(self.num_of_tricks[0]) +"\n" +\
                "North " + str(self.num_of_tricks[1]) +"\n" +\
                "East " + str(self.num_of_tricks[2])
        arcade.draw_text(text,
                         turn_msg_x_coord[2], 
                         turn_msg_y_coord[2],
                         arcade.color.BLACK, 
                         font_size=16)

    def on_draw(self):
        """
        Render the screen.
        """
        
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        #super().on_draw()
        
        # Call draw() on all your sprite lists below

        #self.draw_frame()

        
        if self.connecting_stage:
            self.draw_connect()
        else:
            self.button_list[5].disable()
        
        if self.waiting_stage:
            arcade.draw_text("Waiting for other players",
                         200, 
                         400,
                         arcade.color.BLACK, 
                         font_size=20)

        if not self.connecting_stage and not self.waiting_stage:
            self.draw_frame()

        if self.bidding_stage or self.prikup_stage:
            self.draw_bids(self.bids)

        if self.bidding_stage or self.prikup_stage or \
            self.order_stage or self.vist_stage or \
            self.choosing_stage:
            draw_star(star_x_coord[(self.turn + self.my_shift)%3],
                      star_y_coord[(self.turn + self.my_shift)%3])

        if self.bidding_stage and not bidding_complete(self.bids):
            self.draw_slovo()
            if self.bidding_turn == self.my_num:
                self.draw_cont_bidding(self.bids)
            else:
                self.disable_buttons([0,1,2])

        if self.order_stage and self.curr_bid_winner == self.my_num:
                self.draw_order(self.bids)
        else:
            self.disable_buttons([3])

        if self.vist_stage:
            self.draw_bids(self.vists)
            if self.visting_turn == self.my_num:
                self.draw_visting()
            else:
                self.disable_buttons([6,7])
        else:
             self.disable_buttons([6,7])

        if self.choosing_stage:
            visting_num = self.vists.index("вист")
            if self.my_num == visting_num:
                self.button_list[8].draw()
                self.button_list[9].draw()
                self.disable_buttons([0,1,2])
            else:
                name = self.players[visting_num]
                temp = name + " выбирает, в открытую или взакрытую"
                arcade.draw_text(temp, 200,300, 
                                arcade.color.BLACK,font_size=16)
                self.disable_buttons([0,1,2,8,9])
        else:
             self.disable_buttons([8,9])
       
        if self.new_round_stage:
            self.draw_continue()
            self.disable_buttons([12,13])

        if self.playing_stage:
            self.draw_playing()

        if self.writing_stage:
            self.draw_writing()
            self.deal_new_round() #MS!!!
            self.turn = (self.turn + 1)%3   
    

        if self.show_stage:
            self.shape_list.draw()
            self.score.write_pool(320,300,600,400,self.my_shift)
            """
            write_pool(320,300,600,400,
                       self.pool,self.hill,self.vist_counts)
            """

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        super().on_update(delta_time)
        
        if self.client.got_udp_msg:
            self.parse_server_msg()
        #добавить распас и т.д.
        if bidding_complete(self.bids) and self.bidding_stage:
            self.bidding_stage = 0 
            self.curr_bid_winner = who_won_bidding(self.bids)
            if self.curr_bid_winner >= 0: #not распас
                self.vists[self.curr_bid_winner] =\
                    self.bids[self.curr_bid_winner] #temporary
                self.visting_turn = (self.curr_bid_winner+1)%3
                
                if self.bids[self.curr_bid_winner] == "мизер":
                    temp = "miser"
                elif self.bids[self.curr_bid_winner] == "мизер БП":
                    temp = "miser_bp"
                else:
                    temp="reg"
            else:
                temp="raspas"
            if self.my_num == self.turn: #send only once
                message ={"bidding_winner":str(self.curr_bid_winner),
                          "type":str(temp)}
                self.client.send(message, "server")

        if self.vist_complete:
            self.finalize_vists()

        self.disable_unnecessary_buttons() #MS!!!

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        super().on_key_press(key, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        super().on_key_release(key, key_modifiers)

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        super().on_mouse_motion(x, y, delta_x, delta_y)
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        if self.playing_stage:
            #self.check_trick(x,y)
            self.put_card(x,y)
            if button == arcade.MOUSE_BUTTON_RIGHT:
                self.collect_trick(x,y)

        if self.prikup_stage:
            if button == arcade.MOUSE_BUTTON_LEFT:
                #MS!!! do I want left and right?
                self.collect_prikup(x,y)
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                self.collect_prikup(x,y)

        self.discard_prikup(x,y)

        check_mouse_press_for_buttons(x, y, self.button_list)

        super().on_mouse_press(x, y, button, key_modifiers)
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        check_mouse_release_for_buttons(x, y, self.button_list)
        super().on_mouse_release(x, y, button, key_modifiers)

    def put_card(self, x, y):
        j = self.current_turn
        if j != self.my_num:
            return
        if self.current_trick[j] != 0:
            return
        i = card_chosen(self.hand,x,y)
        if i > -1:
            card = self.hand[i]
            #set suit by first card and allow any card
            if self.how_many_cards_in_trick() == 0 and \
                self.current_trick[3] == "n":
                self.current_trick[3] = card.suit 
            if has_suit(self.hand,self.current_trick[3]) and\
                card.suit != self.current_trick[3]:
                return
            #current_trick[3] holds suit of the current trick
            elif not has_suit(self.hand,self.current_trick[3]) and\
                has_suit(self.hand,self.current_round["trump"]) and\
                card.suit != self.current_round["trump"]:
                return

            self.add_card_to_trick(card, i, j)

            self.send_card(card.num, i, self.current_trick[3])

    def add_card_to_trick(self, card, i, player_num):
        self.current_trick[player_num] = card
        self.current_trick_list.append(card.face)
        if player_num == self.my_num:
            self.hand.pop(i) #MS!!!
            self.south_list.pop(i) 
            card.set_south_trick_coord()
        elif player_num == (self.my_num + 1)%3:
            self.north_list.pop(i) 
            card.set_north_trick_coord()
        elif player_num == (self.my_num + 2)%3:
            self.east_list.pop(i) 
            card.set_east_trick_coord()

        if self.how_many_cards_in_trick() == 3:
            self.current_turn = -1
        else:
            self.current_turn = (player_num + 1)%3


    def send_card(self, num, i, suit):
        message = {"player_number":str(self.my_num),
                   "card_num":str(num),
                   "sprite_num":str(i),
                   "suit":str(suit)}
        self.client.send(message)

    def how_many_cards_in_trick(self):
        num = 0
        for i in [0,1,2]:
            if self.current_trick[i] != 0:
                num += 1
        return(num)

    def collect_trick(self,x,y):
        #Click right mouse button
        if self.how_many_cards_in_trick() != 3:
            return #not all players have put down a card
        hand = self.current_trick[0:3]
        if card_chosen(hand,x,y) > -1:
            winner = find_winner(hand, 
                                 self.current_round["trump"], 
                                 self.current_trick[3])
            if winner != self.my_num:
                return
            self.send_trick_winner(winner)
            self.remove_trick(winner)

    def remove_trick(self, winner):
        new_trick = Trick(self.current_trick[3],self.current_round["trump"],
                          self.current_trick[0:3])
            
        new_trick.set_coord((winner + self.my_shift)%3,
                            self.num_of_tricks[winner])
        
        self.num_of_tricks[winner] += 1
        for i in [0,1,2]:
            self.collected_tricks_list.append(new_trick.cards[i].back)
            self.current_trick_list.pop()
            self.current_trick[i] = 0
        if self.current_round["type"] == "raspas" and \
            self.times_prikup_opened == 1:
            self.prikup_list.pop(1)
            self.open_prikup(0)
            self.current_trick[3] = self.prikup[0].suit
            self.current_turn = self.turn
        elif self.current_round["type"] == "raspas" and \
            self.times_prikup_opened == 2:
            self.prikup_list.pop()
            self.times_prikup_opened = 0
            self.current_trick[3] = "n"
            self.current_turn = winner
        else:
            self.current_trick[3] = "n"
            self.current_turn = winner

        if self.round_finished():
            #self.playing_stage = 0 #MS!!!
            self.new_round_stage = 1

    def round_finished(self):
        sum = self.num_of_tricks[0] + \
            self.num_of_tricks[1] + self.num_of_tricks[2]
        if sum == 10:
            return True
        else:
            return False

    def connect(self):
        pass
        #self.order_stage = 0
        #print(self.order_stage)

    def bid_reg(self):
        #self.order_stage = 0 MS???
        if self.button_list[1].text == "стоп":
            self.bids[self.bidding_turn] = "пас"
        else:
            self.bids[self.bidding_turn] = self.button_list[1].text
        #move turn to the next player
        self.bidding_turn = (self.bidding_turn + 1)%3

        # Next index in bidding_order
        self.bidding_index +=1

        self.send_bid()

    def bid_miser(self):
        #Network send "мизер" or "мизер БП"
        self.bids[self.bidding_turn] = self.button_list[0].text
        #and move turn to next player
        self.bidding_turn = (self.bidding_turn + 1)%3
        if self.button_list[0].text == "мизер":
            #Bidding starts with 9 spades
            self.bidding_index=15
        else: #"мизер БП"
            #Bidding starts with 10 spades
            self.bidding_index=20
        self.send_bid()

    def bid_pas(self):
        self.bids[self.bidding_turn] = "пас"
        # Через пасующего говорят "здесь"
        i = (self.bidding_turn - 1)%3
        if self.bidding_index > 1 and self.bids[i] != "мизер" \
            and self.bids[i] != "мизер БП":
            self.bidding_index -=1
        #and move turn to the next player
        self.bidding_turn = (self.bidding_turn + 1)%3
        #Network send "Pas"
        self.send_bid()

    def send_bid(self):
        message = {"player_number":str(self.my_num),
                   "bid":self.bids[self.my_num],
                   "bidding_turn":str(self.bidding_turn),
                   "bidding_index":str(self.bidding_index)}
        self.client.send(message)

    def send_vist(self):
        self.vists[self.visting_turn] = "вист"
        self.visting_turn = (self.visting_turn + 1)%3
        self.times_vist_sent += 1
        if self.times_vist_sent > 1:
            self.vist_complete = 1
        
        message = {"player_number":str(self.my_num),
                   "vist":"вист",
                   "visting_turn":str(self.visting_turn),
                   "times_vist_sent":str(self.times_vist_sent),
                   "vist_complete":str(self.vist_complete)}
        self.client.send(message)

    def send_vist_pas(self):
        self.vists[self.visting_turn] = self.button_list[7].text
        self.visting_turn = (self.visting_turn + 1)%3
        self.times_vist_sent += 1

        if self.button_list[7].text == "свой":
            self.visting_turn = (self.visting_turn + 1)%3
        elif self.times_vist_sent > 1:
            self.vist_complete = 1

        message = {"player_number":str(self.my_num),
                   "vist":str(self.button_list[7].text),
                   "visting_turn":str(self.visting_turn),
                   "times_vist_sent":str(self.times_vist_sent),
                   "vist_complete":str(self.vist_complete)}
        self.client.send(message)

    def send_open(self):
        # I am visting, get pasing player number
        # it occurs only once in this case
        pasing_num = self.vists.index("пас")
        print("pasing_num = ",pasing_num)
        message = {"player_number":str(self.my_num),
                   "how":"open",
                   "pasing_num":str(pasing_num),
                   "playing_num":str(self.curr_bid_winner)}      
        self.client.send(message, "server")

    def send_closed(self):
        message = {"player_number":str(self.my_num),
                   "how":"closed"}  
        self.client.send(message)
        self.choosing_stage = 0
        self.playing_stage = 1

    def send_continue(self):
        self.clear_sprite_lists()
        self.new_round_stage = 0
        self.playing_stage = 0
        self.waiting_stage = 1
        message = {"player_number":str(self.my_num),
                   "next":"next"}
        self.client.send(message, "server")

    def send_offer(self):
        how_many = int(self.textbox_list[2].text_storage.text)

        if how_many < 0 or how_many > 10:
            return
        
        message = {"player_number":str(self.my_num),
                   "offer":str(how_many)}
        self.client.send(message)
        self.setup_current_offer(self.my_num, how_many)

    def setup_current_offer(self, num, offer):
        self.offered_to_end_round = 1
        self.current_offer["value"] = offer
        self.current_offer["offering_hand"] = num
        
        for i in [0,1,2]:
            if self.vists[i] != "пас" and i != num:
                self.current_offer["accepting_hand"] = i
                break
        
    def send_yes(self):
        self.new_round_stage = 1
        self.offered_to_end_round = 0
        self.disable_buttons([12,13])
        message = {"player_number":str(self.my_num),
                   "answer":"yes"}
        self.client.send(message) 

    def send_no(self):
        self.offered_to_end_round = 0
        self.disable_buttons([12,13])
        message = {"player_number":str(self.my_num),
                   "answer":"no"}
        self.client.send(message)  

    def send_trick_winner(self, winner):
        message = {"player_number":str(self.my_num),
                   "trick_winner":str(winner)}
        self.client.send(message)

    def finalize_vists(self):
        i = self.curr_bid_winner
        #name = self.players[self.curr_bid_winner]
        #game = self.vists[self.curr_bid_winner]
        if self.vists[(i+1)%3] == "вист" and self.vists[(i+2)%3] == "свой":
            self.vists[(i+2)%3] = "пас"
        vist_sum = 0
        for vist in self.vists:
            if vist == "вист":
                vist_sum += 1
        if vist_sum == 0:
            self.new_round_stage = 1
        elif vist_sum == 1:
            self.choosing_stage = 1
        else: #both vist
            self.playing_stage = 1

        self.vist_stage = 0
        self.vist_complete = 0

        

    def show_pool(self):
        self.show_stage = (self.show_stage + 1)%2

    def send_order(self):
        order = self.textbox_list[0].text_storage.text
        index = game_order_check(self.bids, order)

        if index == -1:
            self.order_stage = 1
        else:
            self.move_to_vist_stage(order, index)
            message = {"player_number":str(self.my_num),
                       "playing":str(order),
                       "index":str(index)}
            self.client.send(message)
            
    def move_to_vist_stage(self, order, index):
        self.order_stage = 0
        self.vist_stage = 1
        #set trump, for instance, "c" for 6c, "n" for 7n, etc
        #n being no trumps, and set value
        if int(order[0]) == 1:
            self.current_round["value"] = 10
            self.current_round["trump"] = order[2]
        else:
            self.current_round["trump"] = order[1]
            self.current_round["value"] = int(order[0])
        self.current_round_type = order #MS!!! fix this!

        self.vists[self.curr_bid_winner] = bidding_order[index]

    def send_name(self):
        name = self.textbox_list[1].text_storage.text
        self.client.name = name
        print(name)
        self.connect_to_server()
        self.connecting_stage = 0
        self.waiting_stage = 1

    def disable_unnecessary_buttons(self):
        if not self.connecting_stage:
            self.button_list[5].disable()
        if not self.bidding_stage:
            self.disable_buttons([0,1,2])
        if not self.order_stage:
            self.button_list[3].disable()
        if not self.vist_stage:
            self.disable_buttons([6,7])
        if not self.choosing_stage:
            self.disable_buttons([8,9])
        if not self.new_round_stage:
            self.button_list[10].disable()
        if not self.playing_stage:
            self.disable_buttons([11,12,13])
        if not self.offered_to_end_round:
            self.disable_buttons([12,13])

    def close(self):
        """ Close the Window. """
        super().close()
        
        self.client.leave_room()
        self.client.server_listener.stop()
        


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
