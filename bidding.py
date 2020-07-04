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

visting_order = ["пас","свой","вист","играет"] #MS!!!

"""
turn_msg_x_coord = [10,10,700]
turn_msg_y_coord = [200,400,70]

bid_msg_x_coord = [70,70,700]
bid_msg_y_coord = [200,400,50]

star_x_coord = [turn_msg_x_coord[0]+5,
                turn_msg_x_coord[1]+5, 665]
star_y_coord = [turn_msg_y_coord[0]-20,
                turn_msg_y_coord[1]+30, 345]
"""
turn_msg_x_coord = [10,10,600]
turn_msg_y_coord = [200,400,305]

bid_msg_x_coord = [70,70,600]
bid_msg_y_coord = [200,400,285]

star_x_coord = [turn_msg_x_coord[0]+5,
                turn_msg_x_coord[1]+5, 640]
star_y_coord = [turn_msg_y_coord[0]-20,
                turn_msg_y_coord[1]+30, 345]

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
        self.enabled = False

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
        self.enable() 

    def on_press(self):
        self.pressed = True

    def on_release(self):
        self.pressed = False

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True


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
            
class RegularButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 90, 30, text, 18, "Arial")
        self.action_function = action_function
        self.text = text
        
    def on_release(self):
        super().on_release()
        if self.enabled:
            self.action_function()

class WideButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 130, 30, text, 18, "Arial")
        self.action_function = action_function
        self.text = text
        
    def on_release(self):
        super().on_release()
        if self.enabled:
            self.action_function()

class ShowPoolButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 70, 30, "Показать\n пулю", 18, "Arial")
        self.action_function = action_function
        self.text = text
        self.font_size = 12 #was 142, 30

    def on_release(self):
        super().on_release()
        if self.text == "Показать\n пулю":
            self.text = "Скрыть\n пулю"
        else:
            self.text = "Показать\n пулю"
        if self.enabled:
            self.action_function()

class LastTrickButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 140, 30, "Показать посл взятку", 18, "Arial")
        self.action_function = action_function
        self.text = text
        self.font_size = 12 #was 142, 30

    def on_release(self):
        super().on_release()
        if self.text == "Показать посл взятку":
            self.text = "Скрыть посл взятку"
        else:
            self.text = "Показать посл взятку"
        if self.enabled:
            self.action_function()

class SmallButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 70, 30, "Расписать\n пулю", 18, "Arial")
        self.action_function = action_function
        self.text = text
        self.font_size = 12 

    def on_release(self):
        super().on_release() 
        if self.enabled:
            self.action_function()    

class ConnectButton(TextButton):
    def __init__(self, center_x, center_y, action_function, text):
        super().__init__(center_x, center_y, 90, 30, "Играть", 18, "Arial")
        self.action_function = action_function
        self.text = text

    def on_release(self):
        super().on_release()
        if self.enabled:
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
    #in case of "распас" this function returns -1
    i = 0
    for bid in bids:
        if bid != "пас":
            return i
        i += 1
    return -1
    

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
    if index < bid_index:
        return -1
    else:
        return index
