import arcade
SF = .11
from random import shuffle
#num,value,suit,face
picz = [[0,7,"s","sprites/cards/7_of_spades.png"],
        [1,8,"s","sprites/cards/8_of_spades.png"],
        [2,9,"s","sprites/cards/9_of_spades.png"],
        [3,10,"s","sprites/cards/10_of_spades.png"],
        [4,11,"s","sprites/cards/jack_of_spades2.png"],
        [5,12,"s","sprites/cards/queen_of_spades2.png"],
        [6,13,"s","sprites/cards/king_of_spades2.png"],
        [7,14,"s","sprites/cards/ace_of_spades2.png"],

        [8,7,"c","sprites/cards/7_of_clubs.png"],
        [9,8,"c","sprites/cards/8_of_clubs.png"],
        [10,9,"c","sprites/cards/9_of_clubs.png"],
        [11,10,"c","sprites/cards/10_of_clubs.png"],
        [12,11,"c","sprites/cards/jack_of_clubs2.png"],
        [13,12,"c","sprites/cards/queen_of_clubs2.png"],
        [14,13,"c","sprites/cards/king_of_clubs2.png"],
        [15,14,"c","sprites/cards/ace_of_clubs.png"],

        [16,7,"d","sprites/cards/7_of_diamonds.png"],
        [17,8,"d","sprites/cards/8_of_diamonds.png"],
        [18,9,"d","sprites/cards/9_of_diamonds.png"],
        [19,10,"d","sprites/cards/10_of_diamonds.png"],
        [20,11,"d","sprites/cards/jack_of_diamonds2.png"],
        [21,12,"d","sprites/cards/queen_of_diamonds2.png"],
        [22,13,"d","sprites/cards/king_of_diamonds2.png"],
        [23,14,"d","sprites/cards/ace_of_diamonds.png"],

        [24,7,"h","sprites/cards/7_of_hearts.png"],
        [25,8,"h","sprites/cards/8_of_hearts.png"],
        [26,9,"h","sprites/cards/9_of_hearts.png"],
        [27,10,"h","sprites/cards/10_of_hearts.png"],
        [28,11,"h","sprites/cards/jack_of_hearts2.png"],
        [29,12,"h","sprites/cards/queen_of_hearts2.png"],
        [30,13,"h","sprites/cards/king_of_hearts2.png"],
        [31,14,"h","sprites/cards/ace_of_hearts.png"]
]

class Card:
    def __init__(self,num,value,suit,face):
        self.num = num
        self.value = value
        self.suit = suit
        self.face = face
        self.back = \
            arcade.Sprite("sprites/cards/back_red.png",SF)
        self.trump = 0
        self.face.guid = num

    def set_south_coord(self,order):
        self.face.center_x = 35+60*order
        self.face.center_y = 60

    def set_north_coord(self,order):
        self.face.center_x = 35+60*order
        self.face.center_y = 535
        self.back.center_x = 35+60*order
        self.back.center_y = 535

    def set_east_coord(self,order):
        #y=[535,535,445,445,355,355,265,265,175,175]
        y=[525,525,435,435,345,345,255,255,165,165]
        self.face.center_x = 700+60*(order%2)
        self.face.center_y = y[order]
        self.back.center_x = 700+60*(order%2)
        self.back.center_y = y[order]

    def set_prikup_coord(self,order):
        self.face.center_x = 450+60*order
        self.face.center_y = 300
        self.back.center_x = 450+60*order
        self.back.center_y = 300

    def set_south_trick_coord(self):
        self.face.center_x = 320
        self.face.center_y = 240

    def set_north_trick_coord(self): 
        self.face.center_x = 320
        self.face.center_y = 360

    def set_east_trick_coord(self):
        self.face.center_x = 380
        self.face.center_y = 300
       
def get_key(card):
    if (card.suit == "h"):
        return("u"+str(card.value-6))
    return(card.suit + str(card.value-6))

#This should change with server
deck = []
for i in range(32):
    new_card=Card(picz[i][0], picz[i][1], picz[i][2], \
        arcade.Sprite(picz[i][3],SF))
    deck.append(new_card)

def deal(shuffled_deck, beg_index, end_index, hand):
    del hand[:]
    hand.extend(shuffled_deck[beg_index:end_index])
    hand.sort(reverse=True, key = get_key)

def deal_all_hands(hands):
    shuffle(deck)
    #temp = get_players_order(round_players,round_num)
    for i in [0,1,2]:
        beg_index = 10*i
        end_index =10*(i+1)
        deal(deck, beg_index, end_index, hands[i])
        #prikup
        deal(deck, 30, 32, hands[3])
        #return(temp)

def card_chosen(hand,x,y):
    i = 0
    point = (x,y)
    for card in hand:
        if card.face.collides_with_point(point):
            return(i)
        i += 1
    return(-1)

def has_suit(hand,suit):
    for card in hand:
        if card.suit == suit:
            return(True)
    return(False)

class Trick:
    def __init__(self,suit,trump,cards):
        self.suit = suit
        self.trump = trump
        self.cards = cards

    def set_winner(self):
        if has_suit(self.cards, self.trump):
            win_suit = self.trump
        else:
            win_suit = self.suit
        win_value = 6
        for i in [0,1,2]:
            if self.cards[i].suit != win_suit:
                continue
            if self.cards[i].value > win_value:
                win_value = self.cards[i].value
                winner = i
        return(winner)

    def set_coord(self,winner,num):
        x=[450,510,570,630,450,510,570,630,390,390]
        y=[350,350,350,350,250,250,250,250,350,250]
        k=[-1,1]
        if winner == 0: #south
            for i in [0,1,2]:
                self.cards[i].back.center_x = 35+5*i+60*num
                self.cards[i].back.center_y = 160
                self.cards[i].back.angle = 30*(-1*num%2)
        elif winner == 1: #north
            for i in [0,1,2]:
                self.cards[i].back.center_x = 35+5*i+60*num
                self.cards[i].back.center_y = 435
                self.cards[i].back.angle = 30*(-1*num%2)
        else: #east
            for i in [0,1,2]:
                self.cards[i].back.center_x = x[num]+5*i
                self.cards[i].back.center_y = y[num]
                self.cards[i].back.angle = 30*k[num%2]

  