"""
Buttons are displayed for bidding
"""
import arcade

#should be set up by network
#bids=[0,0,0]
#bidding_turn = [0]
#index = [0]

bidding_order = [\
    "6 пик","6 треф","6 бубей","6 червей","6 БК",
    "7 пик","7 треф","7 бубей","7 червей","7 БК",
    "8 пик","8 треф","8 бубей","8 червей","8 БК",
    "9 пик","9 треф","9 бубей","9 червей","9 БК",
    "10 пик","10 треф","10 бубей","10 червей","10 БК",
    "стоп"]

game_order = [\
    "6s","6c","6d","6h","6n",
    "7s","7c","7d","7h","7n",
    "8s","8c","8d","8h","8n",
    "9s","9c","9d","9h","9n",
    "10s","10c","10d","10h","10n"]

turn_msg_x_coord = [10,10,700]
turn_msg_y_coord = [200,400,70]

bid_msg_x_coord = [70,70,700]
bid_msg_y_coord = [200,400,50]

star_x_coord = [turn_msg_x_coord[0]+5,
                turn_msg_x_coord[1]+5, 685]
star_y_coord = [turn_msg_y_coord[0]-20,
                turn_msg_y_coord[1]+30, 578]



class TextButton:
    """ Text-based button """

    def __init__(self,
                 center_x, center_y,
                 width, height,
                 text,
                 font_size=18,
                 font_face="Arial",
                 face_color=arcade.color.LIGHT_GRAY,
                 highlight_color=arcade.color.WHITE,
                 shadow_color=arcade.color.GRAY,
                 button_height=2):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.font_face = font_face
        self.pressed = False
        self.face_color = face_color
        self.highlight_color = highlight_color
        self.shadow_color = shadow_color
        self.button_height = button_height

    def draw(self):
        """ Draw the button """
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width,
                                     self.height, self.face_color)

        if not self.pressed:
            color = self.shadow_color
        else:
            color = self.highlight_color

        # Bottom horizontal
        arcade.draw_line(self.center_x - self.width / 2, self.center_y - self.height / 2,
                         self.center_x + self.width / 2, self.center_y - self.height / 2,
                         color, self.button_height)

        # Right vertical
        arcade.draw_line(self.center_x + self.width / 2, self.center_y - self.height / 2,
                         self.center_x + self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        if not self.pressed:
            color = self.highlight_color
        else:
            color = self.shadow_color

        # Top horizontal
        arcade.draw_line(self.center_x - self.width / 2, self.center_y + self.height / 2,
                         self.center_x + self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        # Left vertical
        arcade.draw_line(self.center_x - self.width / 2, self.center_y - self.height / 2,
                         self.center_x - self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        x = self.center_x
        y = self.center_y
        if not self.pressed:
            x -= self.button_height
            y += self.button_height

        arcade.draw_text(self.text, x, y,
                         arcade.color.BLACK, font_size=self.font_size,
                         width=self.width, align="center",
                         anchor_x="center", anchor_y="center")

    def on_press(self):
        self.pressed = True

    def on_release(self):
        self.pressed = False


def check_mouse_press_for_buttons(x, y, button_list):
    """ Given an x, y, see if we need to register any button clicks. """
    for button in button_list:
        if x > button.center_x + button.width / 2:
            continue
        if x < button.center_x - button.width / 2:
            continue
        if y > button.center_y + button.height / 2:
            continue
        if y < button.center_y - button.height / 2:
            continue
        button.on_press()


def check_mouse_release_for_buttons(_x, _y, button_list):
    """ If a mouse button has been released, see if we need to process
        any release events. """
    for button in button_list:
        if button.pressed:
            button.on_release()


class MiserButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 90, 30, "мизер", 18, "Arial")
        self.action_function = action_function
        self.text = text

    def on_release(self):
        super().on_release()
        self.action_function()   
    """
    def action_function(self):
        #Network send "мизер" or "мизер БП"
        bids[bidding_turn[0]] = self.text
        #and move turn to next player
        bidding_turn[0] = (bidding_turn[0] + 1)%3
        if self.text == "мизер":
            #Bidding starts with 9 spades
            index[0]=15
        else: #"мизер БП"
            #Bidding starts with 10 spades
            index[0]=20
    """
        
class PasButton(TextButton):
    def __init__(self, center_x, center_y, action_function):
        super().__init__(center_x, center_y, 90, 30, "пас", 18, "Arial")
        self.action_function = action_function

    def on_release(self):
        super().on_release()
        self.action_function()
    """
    def action_function(self):
        #Network send "Pas"
        #and move turn to next player
        bids[bidding_turn[0]] = "пас"
        bidding_turn[0] = (bidding_turn[0] + 1)%3
        # Через пасующего говорят "здесь"
        if index[0] > 1:
            index[0] -=1
    """
            
class RegularButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 90, 30, text, 18, "Arial")
        self.action_function = action_function
        self.text = text

    """
    def action_function(self):
        #Network send self.text
        #and move turn to next player
        if self.text == "стоп":
            bids[bidding_turn[0]] = "пас"
        else:
            bids[bidding_turn[0]] = self.text
        bidding_turn[0] = (bidding_turn[0] + 1)%3

        # Next index in bidding_order
        index[0] +=1
    """
    
    
        
    def on_release(self):
        super().on_release()
        self.action_function()


class OrderButton(TextButton):
    def __init__(self, center_x, center_y, action_function):
        super().__init__(center_x, center_y, 90, 30, "заказ", 18, "Arial")
        self.action_function = action_function

    def on_release(self):
        super().on_release()
        self.action_function()


class ShowPoolButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 142, 30, "Показать пулю", 18, "Arial")
        self.action_function = action_function
        self.text = text

    def on_release(self):
        super().on_release()
        if self.text == "Показать пулю":
            self.text = "Скрыть пулю"
        else:
            self.text = "Показать пулю"
        self.action_function()   
    """
    def action_function(self):
        if self.text == "Показать пулю":
            self.text = "Скрыть пулю"
        else:
            self.text = "Показать пулю"
    """

class ConnectButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 90, 30, "Играть", 18, "Arial")
        self.action_function = action_function
        self.text = text

    def on_release(self):
        super().on_release()
        self.action_function()   
        

def bidding_complete(bids):
    number_pases = 0
    for bid in bids:
        if bid == 0:
            return False
        if bid == "пас":
            number_pases += 1
    if number_pases >= 2:
        return True
    else:
        return False

def who_won_bidding(bids):
    #there's already only one winner, others have "пас"
    #in case of "распас" this function won't be called
    i = 0
    for bid in bids:
        if bid != "пас":
            return i
        i += 1
    if i > 2:
        #this could not happen
        return 0
    

def game_order_check(bids,order):
    #list.index(element)
    index = -1
    for legit_order in game_order:
        if order == legit_order:
            index = game_order.index(legit_order)
            break
    if index == -1: #user typo
        return index
    for bid in bids:
        if bid != "пас":
            bid_index = bidding_order.index(bid)
            break
    #print("bid_index=",bid_index," index=",index)
    if index < bid_index:
        return -1
    else:
        return index

"""
def get_bid(i, avail_bid, bids):
	#bidding goes in order; miser at any time
	#9 trumps miser; miser_bp trumps 9;
	#10 trumps miser_pb
	# cherez pasuyuscego mozhno govorit' zdes' -
	#repeat previous bid
		
	if bids[i] == 0 and bids[(i+1)%3] != "miser"\
	   and bids[(i+2)%3] != "miser":
       #Miser button should exist
       pass
		
	elif bids[i] == "miser":
        #User pressed "Miser" before
        #Button should show "Miser bez prikupa"
		pass
	elif bids[i] != "miser_bp":
		#No Miser Button
        pass
	
	value = 0
	while not PromptPasses(value, AcceptableBids):
		value = input(myStr)
	myStr = RoundPlayers[i]+" bid " + value + " \n"
	print(myStr)
	if value == "miser":
		newAvailBid = 15
	elif value == "miser_bp":
		newAvailBid = 20
	elif Bids[(i+1)%3] == "pas": #cherez pasuyscego zdes'
		newAvailBid = availBid
	else:
		newAvailBid = availBid + 1
		
	Bids[i] = value

	#Force pas if bids exhausted
	if newAvailBid == 25:
		Bids[(i+1)%3]="pas"
		Bids[(i+2)%3]="pas"
		
	return(newAvailBid)


def AllRoundsOfBids(Bids):
	availBid = 0
	while 1:
		for i in [0,1,2]:
			if BiddingComplete(Bids):
				return
			if Bids[i] != "pas":
				availBid = GetBid(i, availBid, Bids)
"""