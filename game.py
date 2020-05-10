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

from datetime import datetime
from random import seed
from random import randint
from random import shuffle
#seed(1)
seed(datetime.now())

hands = [[],[],[],[]]

# Пуля: Юг, Север, Восток
pool = [0,0,0]
# Гора: Юг, Север, Восток
hill = [20,20,20]
# Висты: юг на север и т.д.
#[[S/N,S/E],[N/S,N/E],[E/S,E/N]
vists = [[10,20],[30,40],[50,60]]

stack=[]
for i in range(32):
    stack.append(i)

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

        self.text = ""
        self.suit = ""
        self.turn = 0 #South starts, fix later!!! Server
        self.current_turn = 0 #trick winner
        self.bidding_turn = self.turn
        self.bidding_index = 0

        self.bids=[0,0,0]
        self.current_trick = [0,0,0,"n"]
        self.num_of_tricks = [0,0,0]

        self.connected = 0 #change!!!

        #stages
        self.connecting_stage = 1 #connecting to server
        self.dealing_stage = 0
        self.bidding_stage = 0
        self.prikup_stage = 0
        self.order_stage = 0
        self.vist_stage = 0
        self.open_cards_stage = 0
        self.playing_stage = 0
        self.writing_stage = 0
        self.show_stage = 0

        self.times_prikup_opened = 0
        self.times_prikup_collected = 0
        self.times_prikup_discarded = 0

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

        #self.miser_text = "мизер"
        #self.reg_text = "6 пик"

        self.round_num = 0
        
        #self.round_num = deal_all_hands(hands,self.round_num)
        deal_all_hands(hands)

    def init_round(self):
        self.text = ""
        self.suit = ""
        
        self.current_turn = 0 #trick winner
        self.bidding_turn = self.turn
        self.bidding_index = 0

        self.bids=[0,0,0]
        self.current_trick = [0,0,0,"n"]
        self.num_of_tricks = [0,0,0]

        #stages
        self.dealing_stage = 1
        self.bidding_stage = 0
        self.prikup_stage = 0
        self.order_stage = 0
        self.vist_stage = 0
        self.open_cards_stage = 0
        self.playing_stage = 0
        self.writing_stage = 0
        self.show_stage = 0

        self.times_prikup_opened = 0
        self.times_prikup_collected = 0
        self.times_prikup_discarded = 0

    def open_prikup(self,x,y):
        #Click left mouse button
        i = card_chosen(hands[3],x,y)
        if i > -1:
            self.prikup_list.pop(i)
            self.prikup_list.insert(i,hands[3][i].face)
            self.times_prikup_opened += 1

    def collect_prikup(self,x,y):
        if self.times_prikup_opened < 2:
            return
        #Click right mouse button
        i = card_chosen(hands[3],x,y)
        if i > -1:
            self.prikup_list.pop(i)

            n=len(hands[0]) #replace hands[0]!!!
            hands[0].append(hands[3][i])

            self.south_list.append(hands[0][n].face)
            hands[0][n].set_south_coord(n)

            hands[0].sort(reverse=True, key = get_key)

            for j in range(len(hands[0])):
                self.south_list.pop()
            for j in range(len(hands[0])):
                self.south_list.append(hands[0][j].face)
                hands[0][j].set_south_coord(j)

            hands[3].pop(i)
            self.times_prikup_collected += 1
            
    def discard_prikup(self,x,y):
        if self.times_prikup_opened < 2:
            return
        #Click left or right mouse button
        if len(hands[0]) > 10:
            i = card_chosen(hands[0],x,y) #replace hands[0]!!!
            if i > -1:
                self.south_list.pop(i)
                hands[0].pop(i)
                self.times_prikup_discarded += 1
        if self.times_prikup_discarded == 2:

            hands[0].sort(reverse=True, key = get_key)

            for j in range(len(hands[0])):
                self.south_list.pop()
            for j in range(len(hands[0])):
                self.south_list.append(hands[0][j].face)
                hands[0][j].set_south_coord(j)

            self.times_prikup_opened = 0
            self.times_prikup_collected = 0
            self.times_prikup_discarded = 0
            self.prikup_stage = 0
            self.order_stage = 1

    def create_sprite_list(self):
        self.south_list = arcade.SpriteList()
        self.north_list = arcade.SpriteList()
        self.east_list = arcade.SpriteList()
        self.prikup_list = arcade.SpriteList()
        self.current_trick_list = arcade.SpriteList()
        self.collected_tricks_list = arcade.SpriteList()


    def create_button_list(self):
        self.button_list = []
        
        miser_button = MiserButton(70, 150, self.send_miser, "мизер")
        reg_button = RegularButton(210, 150, self.send_bid, "6 пик")
        pas_button = PasButton(350, 150, self.send_pas)
        order_button = OrderButton(250, 300, self.send_order)
        show_pool_button = ShowPoolButton(710, 12, self.show_pool, "Показать пулю")
        connect_button = ConnectButton(500,400,self.connect, "Играть")
            
        self.button_list.append(miser_button)
        self.button_list.append(reg_button)
        self.button_list.append(pas_button)
        self.button_list.append(order_button)
        self.button_list.append(show_pool_button)
        self.button_list.append(connect_button)
            
    def setup(self):
        # Create your sprites and sprite lists here
        self.create_sprite_list()

        # Create our on-screen GUI buttons
        self.create_button_list()
        
        self.textbox_list.append(arcade.TextBox(70, 300, width=60,\
            theme=arcade.Theme(),font_size=16))
        self.textbox_list.append(arcade.TextBox(200, 400, width=200,\
            theme=arcade.Theme(),font_size=16))
          

        #for drawing the pool
        self.shape_list = make_pool(320,300,600,400)                                 
        
        shuffle(stack)
        self.deal_new_round()
       # print(stack)   
          
    def deal_new_round(self):
        for i in range(10):
            self.south_list.append(hands[0][i].face)
            hands[0][i].set_south_coord(i)
            self.north_list.append(hands[1][i].face)
            hands[1][i].set_north_coord(i)
            self.east_list.append(hands[2][i].face)
            hands[2][i].set_east_coord(i)

        for i in [0,1]:
            self.prikup_list.append(hands[3][i].back)
            hands[3][i].set_prikup_coord(i)
            
        self.init_round()

        self.dealing_stage = 0
        self.bidding_stage = 1

    def draw_connect(self):
        temp = "Please type your name in latin alphabet"
        arcade.draw_text(temp, 200,600, arcade.color.BLACK,font_size=16)
        self.textbox_list[1].draw()
        self.button_list[5].draw()

    def draw_frame(self):
        arcade.draw_text("Я-South",250,1,[0,0,0])
        arcade.draw_text("North",250,580,[0,0,0])
        arcade.draw_text("East",700,570,[0,0,0])

        #Always show "Показать пулю" Button
        self.button_list[4].draw()

        self.north_list.draw()
        self.south_list.draw()
        self.east_list.draw()
        self.prikup_list.draw()

        """
        #fix for each player!!!
        for i in [0,1,2]:
            draw_star(star_x_coord[i],star_y_coord[i])
        """


    def draw_order(self, bids):
        i = who_won_bidding(bids)
        
        
        temp = "заказать " + str(bids[i]) +\
                " или выше\ntype 6s for 6 пик, 7c for 7 треф,\n" +\
                "8d for 8 бубей, 9h for 9 червей,\n" +\
                "10n for 10 без козыря и т.д."
        
        arcade.draw_text(temp, 40,200, arcade.color.BLACK,font_size=16)
        self.textbox_list[0].draw()
        self.button_list[3].draw()

    def draw_bids(self, bids):
        for i in[0,1,2]: 
                if bids[i] != 0:
                    arcade.draw_text(bids[i],
                        bid_msg_x_coord[i],
                        bid_msg_y_coord[i],
                        arcade.color.BLACK,
                        font_size=16)

    def draw_cont_bidding(self,bids):
        i = self.bidding_turn
        arcade.draw_text("Слово:",
                         turn_msg_x_coord[i], 
                         turn_msg_y_coord[i],
                         arcade.color.BLACK,
                         font_size=16)

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

    def draw_playing(self):
        arcade.draw_text(self.text,
                         bid_msg_x_coord[2], 
                         bid_msg_y_coord[2],
                         arcade.color.BLACK,
                         font_size=16)
        self.current_trick_list.draw()
        self.collected_tricks_list.draw()

    def draw_writing(self):
        #self.num_of_tricks
        self.text = "South " + str(self.num_of_tricks[0]) +"\n" +\
                "North " + str(self.num_of_tricks[1]) +"\n" +\
                "East " + str(self.num_of_tricks[2])
        arcade.draw_text(self.text,
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

        self.draw_frame()

        """
        if self.connecting_stage:
            self.draw_connect()
        """

        if self.order_stage:
            self.draw_order(self.bids)

        if self.bidding_stage or self.prikup_stage:
            self.draw_bids(self.bids)
            draw_star(star_x_coord[self.turn],
                      star_y_coord[self.turn])

        if self.bidding_stage and not bidding_complete(self.bids):
            self.draw_cont_bidding(self.bids)
            
        if self.playing_stage:
            self.draw_playing()

        if self.writing_stage:
            self.draw_writing()
            deal_all_hands(hands)
            self.deal_new_round() 
            self.turn = (self.turn + 1)%3   
    

        if self.show_stage:
            self.shape_list.draw()
            write_pool(320,300,600,400,pool,hill,vists)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        super().on_update(delta_time)
        #добавить распас и т.д.
        if bidding_complete(self.bids) and self.bidding_stage: 
            self.bidding_stage = 0
            self.prikup_stage = 1
        if len(hands[0]) == 0 and len(hands[1]) == 0 and len(hands[2]) == 0:
            self.playing_stage = 0
            self.writing_stage = 1

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
            self.check_trick(x,y)
            if button == arcade.MOUSE_BUTTON_RIGHT:
                self.collect_trick(x,y)

        if self.prikup_stage:
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.open_prikup(x,y)
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

    def check_trick(self, x, y):
        for j in [0,1,2]:
            if self.current_trick[j] != 0 or self.whose_turn() != j:
                continue
            i = card_chosen(hands[j],x,y)
            if i > -1:
                card = hands[j][i]
                #set suit by first card and allow any card
                if j == self.current_turn:
                    self.suit = card.suit
                elif has_suit(hands[j],self.suit) and\
                    card.suit != self.suit:
                    continue
                #current_trick[3] holds trump
                elif not has_suit(hands[j],self.suit) and\
                    has_suit(hands[j],self.current_trick[3]) and\
                    card.suit != self.current_trick[3]:
                    continue 
                hands[j].pop(i)
                self.current_trick[j] = card
            
                self.current_trick_list.append(card.face)
                if j==0:
                    self.south_list.pop(i) 
                    card.set_south_trick_coord()
                elif j==1:
                    self.north_list.pop(i) 
                    card.set_north_trick_coord()
                else:
                    self.east_list.pop(i) 
                    card.set_east_trick_coord()
                
        
    def whose_turn(self):
        i = self.current_turn
        if self.current_trick[0] == 0 and\
            self.current_trick[1] == 0 and\
            self.current_trick[2] == 0:
            # first hand turn
            return(i)
        if self.current_trick[i] != 0 and\
            self.current_trick[(i+1)%3] == 0 and\
            self.current_trick[(i+2)%3] == 0:
            return((i+1)%3)
        if self.current_trick[i] != 0 and\
            self.current_trick[(i+1)%3] != 0 and\
            self.current_trick[(i+2)%3] == 0:
            return((i+2)%3)
        if self.current_trick[i] != 0 and\
            self.current_trick[(i+1)%3] != 0 and\
            self.current_trick[(i+2)%3] != 0:
            return(3)
        return(-1)

    def collect_trick(self,x,y):
        if self.whose_turn() != 3:
            return #not all players have put down a card
            
        #Click right mouse button
        
        hand = self.current_trick[0:3]
        if card_chosen(hand,x,y) > -1:
            new_trick = Trick(self.suit,self.current_trick[3],\
                self.current_trick[0:3])
            winner = new_trick.set_winner()
            new_trick.set_coord(winner,self.num_of_tricks[winner])
            self.num_of_tricks[winner] += 1
            for i in [0,1,2]:
                self.collected_tricks_list.append(new_trick.cards[i].back)
                self.current_trick_list.pop()
                self.current_trick[i] = 0
            self.current_turn = winner

    def connect(self):
        pass
        #self.order_stage = 0
        #print(self.order_stage)

    def send_bid(self):
        self.order_stage = 0
        #Network send self.text
        #and move turn to next player
        if self.button_list[1].text == "стоп":
            self.bids[self.bidding_turn] = "пас"
        else:
            self.bids[self.bidding_turn] = self.button_list[1].text
        self.bidding_turn = (self.bidding_turn + 1)%3

        # Next index in bidding_order
        self.bidding_index +=1

    def send_miser(self):
        #Network send "мизер" or "мизер БП"
        self.bids[self.bidding_turn] = self.button_list[0].text
        #self.bids[self.bidding_turn] = self.miser_text
        #and move turn to next player
        self.bidding_turn = (self.bidding_turn + 1)%3
        if self.button_list[0].text == "мизер":
            #Bidding starts with 9 spades
            self.bidding_index=15
        else: #"мизер БП"
            #Bidding starts with 10 spades
            self.bidding_index=20

    def send_pas(self):
        #Network send "Pas"
        #and move turn to next player
        self.bids[self.bidding_turn] = "пас"
        self.bidding_turn = (self.bidding_turn + 1)%3
        # Через пасующего говорят "здесь"
        if self.bidding_index > 1:
            self.bidding_index -=1

    def show_pool(self):
        self.show_stage = (self.show_stage + 1)%2

    def send_order(self):
        self.text = self.textbox_list[0].text_storage.text
        index = game_order_check(self.bids,self.text)

        if index == -1:
            self.order_stage = 1
        else:
            self.order_stage = 0
            #self.vist_stage = 1 #later!!!
            self.playing_stage = 1
            #set trump, for instance, "c" for 6c, etc
            self.current_trick[3] = self.text[1]
            #set text to print current round, fix south!!!
            self.text = "South\nиграет\n"+bidding_order[index]


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
