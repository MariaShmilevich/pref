#pool
import arcade

def make_pool(center_x, center_y, width, height):
    radius = 50

    top_right_x = center_x + width/2
    top_right_y = center_y + height/2

    bottom_right_x = center_x + width/2
    bottom_right_y = center_y - height/2

    center_left_x = center_x - width/2
    center_left_y = center_y

    offset_x = center_x - width/2
    offset_y = center_y - height/2

    a = height * (1/5)
    p_width = width*(1-a/height)
    p_height = height-2*a
    p_center_x = offset_x + p_width/2
    p_center_y = center_y
    
    b = height/3
    g_width = width*(1-b/height)
    g_height = height-2*b
    g_center_x = offset_x + g_width/2
    g_center_y = center_y 

    shape_list = arcade.ShapeElementList()
    
    shape = arcade.create_rectangle_filled(center_x,
                                           center_y, 
                                           width, 
                                           height,
                                           arcade.color.WHITE)
    shape_list.append(shape)

    shape = arcade.create_ellipse_outline(center_x,
                                          center_y,
                                          radius,
                                          radius, 
                                          arcade.color.BLACK)

    shape_list.append(shape)


    shape = arcade.create_line(center_x,
                               center_y,
                               top_right_x,
                               top_right_y,
                               arcade.color.BLACK)

    shape_list.append(shape)

    shape = arcade.create_line(center_x,
                               center_y,
                               bottom_right_x,
                               bottom_right_y,
                               arcade.color.BLACK)

    shape_list.append(shape)

    shape = arcade.create_line(center_x,
                               center_y,
                               center_left_x,
                               center_left_y,
                               arcade.color.BLACK)

    shape_list.append(shape)

    shape = arcade.create_rectangle_outline(p_center_x,
                                            p_center_y, 
                                            p_width, 
                                            p_height,
                                            arcade.color.BLACK)

    shape_list.append(shape)

    shape = arcade.create_rectangle_outline(g_center_x,
                                            g_center_y, 
                                            g_width, 
                                            g_height,
                                            arcade.color.BLACK)

    shape_list.append(shape)

    shape = arcade.create_line(p_center_x,
                               offset_y,
                               p_center_x,
                               offset_y + a,
                               arcade.color.BLACK)

    shape_list.append(shape)

    shape = arcade.create_line(p_center_x,
                               offset_y + a + p_height,
                               p_center_x,
                               offset_y + 2*a + p_height,
                               arcade.color.BLACK)

    shape_list.append(shape)

    shape = arcade.create_line(offset_x + p_width,
                               center_y,
                               offset_x + width,
                               center_y,
                               arcade.color.BLACK)

    shape_list.append(shape)

    return shape_list

def draw_star(x, y, color1, color2):
    point_list1 =((x-5,y),
                  (x,y+10),
                  (x+5,y),
                  (x,y-10))
    arcade.draw_polygon_filled(point_list1, color1)
    point_list2 =((x-10,y),
                  (x,y+5),
                  (x+10,y),
                  (x,y-5))
    arcade.draw_polygon_filled(point_list2, color2)

def who_played_miser(who_is_who):
    for i in [0,1,2]:
        if who_is_who[i][0] == "м":
            return i
    return -1

def who_played_round(who_is_who):
    for i in [0,1,2]:
        if who_is_who[i] != "пас" and  \
            who_is_who[i] != "вист" and \
            who_is_who[i] != "свой":
            return i

def who_visted(who_is_who):
    #returns array
    vist_array = []
    for i in [0,1,2]:
        if who_is_who[i] == "вист":
            vist_array.append(i)
    return vist_array

def who_said_svoj(who_is_who):
    for i in [0,1,2]:
        if who_is_who[i] == "свой":
            return i
    return -1

def what_game(who_is_who, i):
    if int(who_is_who[i][0]) == 1:
        return 10
    else:
        return int(who_is_who[i][0]) 

def get_vist_array_index(playing_ind, visting_ind):
    if visting_ind == 0:
        if playing_ind == 1:
            return 0
        else: #playing_ind == 2
            return 1
    elif visting_ind == 1: 
        if playing_ind == 0:
            return 0
        else: #playing_ind == 2
            return 1
    else: #visting_ind == 2: 
        return playing_ind

def get_required_vist_num(game):
    if game == 6:
        return 4
    elif game == 7:
        return 2
    elif game == 8:
        return 1
    elif game == 9:
        return 1
    else:
        return 0
            
                               
class Score:
    def __init__(self, max_pool):
        self.max_pool = max_pool
        self.names = ["","",""]

        #multiplier, becomes 2 when pool is completed
        self.otv_vist_factor = 1 
        #For pool writing:
        # Пуля: Юг, Север, Восток
        self.pool = [0,0,0]
        # Гора: Юг, Север, Восток
        self.hill = [20,20,20]
        # Висты: юг на север и т.д.
        #[[S/N,S/E],[N/S,N/E],[E/S,E/N]
        self.vists = [[0,0],[0,0],[0,0]]
        self.final = [0,0,0]
        self.finished = 0
        self.close_sign = ["","",""]
        #self.close_sign = [">>",">>",">>"]

    def calculate_pool(self, round_type, num_of_tricks, who_is_who):
        if round_type == "raspas":
            for i in [0,1,2]:
                self.hill[i] += num_of_tricks[i] * 2
                if num_of_tricks[i] == 0 and \
                    self.pool[i] < self.max_pool:
                    self.pool[i] += 2
        elif round_type == "miser":
            i = who_played_miser(who_is_who)
            if num_of_tricks[i] == 0:
                if self.otv_vist_factor == 1:
                    remainder = self.add_to_pool(i, 10, [])
                    self.close_pool_if_necessary()
                    self.subtract_from_hill(i, 10 + remainder, [])
                else:
                    self.subtract_from_hill(i, 20, [])
            else:
                self.hill[i] += num_of_tricks[i] * 10
        elif round_type == "bez_treh":
            i = who_played_round(who_is_who)
            self.hill[i] += 12
        else: #reg
            i = who_played_round(who_is_who)
            game = what_game(who_is_who, i)
            game_cost = (game-5)*2
            if num_of_tricks[i] >= game or \
                len(who_visted(who_is_who)) == 0: #pas or svoj
                penalty = 0
            else:
                penalty = game - num_of_tricks[i]
            vist_penalty = self.calculate_vists(num_of_tricks, 
                                  who_is_who, i, game, penalty)
            if penalty > 0:
                self.hill[i] += penalty * game_cost * 2
            else:
                if self.otv_vist_factor == 1:
                    remainder = self.add_to_pool(i, game_cost,
                                                 vist_penalty)
                    self.close_pool_if_necessary()
                    self.subtract_from_hill(i, game_cost + remainder,
                                            vist_penalty)
                else:
                    self.subtract_from_hill(i, game_cost*2,
                                            vist_penalty)
        for i in [0,1,2]:
            if self.pool[i] == self.max_pool:
                self.close_sign[i] =">>"
        if self.time_to_finish_pool():
            self.finish_pool()

    def close_pool_if_necessary(self):
        #it is called only if self.otv_vist_factor is still 1
        num_closed = 0
        last_ind = -1
        for i in [0,1,2]:
            if self.pool[i] == self.max_pool:
                num_closed += 1
            else:
                last_ind = i
        if num_closed <= 1:
            return
        if num_closed == 2:
            self.otv_vist_factor = 2
            #raise the last one
            if last_ind > -1:
                diff = self.max_pool - self.pool[last_ind]
                self.pool[last_ind] = self.max_pool
                self.hill[last_ind] += diff
        elif num_closed == 3:
            self.otv_vist_factor = 2

    def time_to_finish_pool(self):
        num_zero = 0
        for i in [0,1,2]:
            if self.hill[i] == 0 and self.pool[i] == self.max_pool:
                num_zero += 1
        if num_zero > 1:
            return True
        return False

    def add_to_pool(self, i, amount, vist_penalty):
        remainder = 0
        if self.pool[i] < self.max_pool - amount:
            self.pool[i] += amount
        else:
            my_part = self.max_pool - self.pool[i]
            help_part = amount - my_part
            self.pool[i] += my_part
            remainder = self.help_by_pool(i, help_part, vist_penalty)
        return remainder

    def subtract_from_hill(self, i, amount, vist_penalty):
        if self.hill[i] > amount:
            self.hill[i] -= amount
        else:
            help_part = amount - self.hill[i]
            self.hill[i] = 0
            self.help_by_hill(i, help_part, vist_penalty)

    def help_by_pool(self, i, help_part, vist_penalty):
        if len(vist_penalty) == 0 or len(vist_penalty) == 2:
            ind = self.who_else_has_better_pool(i)
            if ind < 0:
                return help_part
            remainder = self.help_pool_iteration(i, ind, help_part)
            if remainder > 0:
                other_ind = 3 - (i + ind)
                remainder = self.help_pool_iteration(i, other_ind, 
                                                     remainder)
        elif len(vist_penalty) == 1:
            other_ind = 3 - (i + vist_penalty[0])
            remainder = self.help_pool_iteration(i, other_ind, 
                                                     help_part)
            if remainder > 0:
                remainder = self.help_pool_iteration(i, vist_penalty[0], 
                                                     remainder)
        return remainder

    def help_pool_iteration(self, helper, recepient, amount):
        remainder = 0
        self.pool[recepient] += amount
        if self.pool[recepient] > self.max_pool:
            remainder = self.pool[recepient] - self.max_pool
            self.pool[recepient] = self.max_pool
        j = get_vist_array_index(recepient, helper)
        self.vists[helper][j] += 10*(amount - remainder)
        return remainder

    def help_by_hill(self, i, help_part, vist_penalty):
        if len(vist_penalty) == 0 or len(vist_penalty) == 2:
            ind = self.who_else_has_better_hill(i)
            if ind == -1:
                #both have 0 MS!!!
                return
            remainder = self.help_hill_iteration(i, ind, help_part)
            if remainder > 0:
                other_ind = 3 - (i + ind)
                remainder = self.help_hill_iteration(i, other_ind, 
                                                     remainder)
        elif len(vist_penalty) == 1:
            other_ind = 3 - (i + vist_penalty[0])
            remainder = self.help_hill_iteration(i, other_ind, 
                                                     help_part)
            if remainder > 0:
                remainder = self.help_hill_iteration(i, vist_penalty[0], 
                                                     remainder)
        return remainder

    def help_hill_iteration(self, helper, recepient, amount):
        remainder = 0
        print(recepient)
        self.hill[recepient] -= amount
        if self.hill[recepient] < 0:
            remainder = 0 - self.hill[recepient]
            self.hill[recepient] = 0
        j = get_vist_array_index(recepient, helper)
        self.vists[helper][j] += 10*(amount - remainder)
        return remainder

    def who_else_has_better_pool(self, helper_ind):
        pool = 0
        index = -1
        #this assures clockwise assignment in case of equal pools
        for i in [(helper_ind+1)%3, (helper_ind+2)%3]:
            if self.pool[i] != self.max_pool and \
                self.pool[i] > pool:
                pool = self.pool[i]
                index = i
        return index

    def who_else_has_better_hill(self, helper_ind):
        hill = 65000
        index = -1
        #this assures clockwise assignment in case of equal hills
        for i in [(helper_ind+1)%3, (helper_ind+2)%3]:
            if self.hill[i] != 0 and \
                self.hill[i] < hill:
                hill = self.hill[i]
                index = i
        return index
        
        
    #returns array of players who have penalty on vists
    #returns empty array if there's no vist penalty
    def calculate_vists(self, num_of_tricks, who_is_who,
                        playing_ind, game, penalty):
        vist_array = who_visted(who_is_who)
        required_vist_num = get_required_vist_num(game)
        vist_penalty_array = []
        if len(vist_array) == 0:
            visting_ind = who_said_svoj(who_is_who)
            if visting_ind > -1:
                i = get_vist_array_index(playing_ind, visting_ind)
                #за 6-ную 2 взятки (8), за 7-ную 1 взятка - тоже 8
                self.vists[visting_ind][i] += 8
            return vist_penalty_array
        elif len(vist_array) == 1: #один вистовал
            pasing_ind = 3 - (playing_ind + vist_array[0])
            i = get_vist_array_index(playing_ind, vist_array[0])
            total_vists = num_of_tricks[vist_array[0]] + \
                num_of_tricks[pasing_ind]
            if game == 10:
                total_vists = 0 #Десятерная не вистуется, только за помощь
            self.vists[vist_array[0]][i] += (game-5)*4* \
                (total_vists + penalty)
            if total_vists < required_vist_num:
                self.hill[vist_array[0]] += \
                    (required_vist_num - total_vists)* \
                        (game-5)*2*self.otv_vist_factor
                vist_penalty_array.append(vist_array[0])
            if penalty > 0:
                i = get_vist_array_index(playing_ind, pasing_ind)
                self.vists[pasing_ind][i] += (game-5)*4*penalty
            return (vist_penalty_array)
        else: #оба вистовали
            punish_vist = False
            total_vists = num_of_tricks[vist_array[0]] + \
                num_of_tricks[vist_array[1]]
            if total_vists < required_vist_num:
                punish_vist = True
                req_half_vist = round(required_vist_num/2+0.1)
            i = get_vist_array_index(playing_ind, vist_array[0])
            self.vists[vist_array[0]][i] += \
                (num_of_tricks[vist_array[0]] + penalty)*(game-5)*4
            if punish_vist and \
                num_of_tricks[vist_array[0]] < req_half_vist:
                self.hill[vist_array[0]] += \
                    (req_half_vist - num_of_tricks[vist_array[0]])* \
                        (game-5)*2*self.otv_vist_factor
                vist_penalty_array.append(vist_array[0])
            i = get_vist_array_index(playing_ind, vist_array[1])
            self.vists[vist_array[1]][i] += \
                (num_of_tricks[vist_array[1]] + penalty)*(game-5)*4
            if punish_vist and \
                num_of_tricks[vist_array[1]] < req_half_vist:
                self.hill[vist_array[1]] += \
                    (req_half_vist - num_of_tricks[vist_array[1]])* \
                        (game-5)*2*self.otv_vist_factor
                vist_penalty_array.append(vist_array[1])
            return vist_penalty_array

    def finish_pool(self):
        bal_vists = [0,0,0]
        for i in [0,1,2]:
            if self.pool[i] < self.max_pool:
                balance = self.max_pool - self.pool[i]
                self.pool[i] = self.max_pool
                self.hill[i] += balance
        amnesty = min(self.hill)
        for i in [0,1,2]:
            self.hill[i] -= amnesty
            bal_vists[i] = round(self.hill[i]*10/3)
        
        #[[0/1,0/2],[1/0,1/2],[2/0,2/1]]
        self.vists[1][0] += bal_vists[0]
        self.vists[2][0] += bal_vists[0]

        self.vists[0][0] += bal_vists[1]
        self.vists[2][1] += bal_vists[1]

        self.vists[0][1] += bal_vists[2]
        self.vists[1][1] += bal_vists[2]

        self.vists[0][0] -= self.vists[1][0]     #0/1 and 1/0
        self.vists[1][0] = (-1)*self.vists[0][0]

        self.vists[0][1] -= self.vists[2][0]     #0/2 and 2/0
        self.vists[2][0] = (-1)*self.vists[0][1]

        self.vists[1][1] -= self.vists[2][1]     #1/2 and 2/1
        self.vists[2][1] = (-1)*self.vists[1][1]

        for i in [0,1,2]:
            self.final[i] = self.vists[i][0] + self.vists[i][1]

        self.finished = 1

    def write_pool(self, center_x, center_y, width, height, shift):
        #shift is actually player's number
        offset_x = center_x - width/2
        offset_y = center_y - height/2
        a = height * (1/5)
        b = height/3
        p_width = width*(1-a/height)
        g_width = width*(1-b/height)

        #Names
        arcade.draw_text(self.names[shift], center_x - 10,
                     center_y - 40,
                     arcade.color.BLACK,
                     font_size=24)
        arcade.draw_text(self.names[(shift+1)%3], center_x - 10,
                     center_y + 15,
                     arcade.color.BLACK,
                     font_size=24)
        arcade.draw_text(self.names[(shift+2)%3], center_x + 25,
                     center_y - 5,
                     arcade.color.BLACK,
                     font_size=24,
                     rotation=90)
        #Pool
        arcade.draw_text(str(self.pool[shift])+self.close_sign[shift],
                             offset_x + 5,
                             offset_y + a + 5,
                             arcade.color.BLACK)
        arcade.draw_text(str(self.pool[(shift+1)%3])+self.close_sign[(shift+1)%3],
                             offset_x + 5,
                             offset_y + height - b + 5,
                             arcade.color.BLACK)
        temp = self.close_sign[(shift+2)%3]
        temp_offset = len(temp)*5
        arcade.draw_text(str(self.pool[(shift+2)%3])+temp,
                             offset_x + p_width - 15 - temp_offset,
                             offset_y + a + 20, #15,
                             arcade.color.BLACK,
                             rotation = 90)

        #Hill
        arcade.draw_text(str(self.hill[shift]),
                             offset_x + p_width/2 - 20,
                             offset_y + b + 5,
                             arcade.color.BLACK)
        arcade.draw_text(str(self.hill[(shift+1)%3]),
                             offset_x + p_width/2 - 20,
                             offset_y + height/2 + 5,
                             arcade.color.BLACK)
        temp = str(self.hill[(shift+2)%3])
        temp_offset = 10 + len(temp)*5
        arcade.draw_text(temp,
                             offset_x + g_width - temp_offset,
                             offset_y + b + 15,
                             arcade.color.BLACK,
                             rotation = 90)

        #Vists
        #S/N, S/E
        #depending on player num, vists' order flips on display
        flip = [[0,0,0],[1,1,0],[0,1,1]]
        f = flip[shift]
        arcade.draw_text(str(self.vists[shift][f[0]]),
                             offset_x + 5,
                             offset_y + 5,
                             arcade.color.BLACK)
        arcade.draw_text(str(self.vists[shift][(f[0]+1)%2]),
                             offset_x + p_width/2 + 5,
                             offset_y + 5,
                             arcade.color.BLACK)

        #N/S, N/E
        arcade.draw_text(str(self.vists[(shift+1)%3][f[1]]),
                             offset_x + 5,
                             offset_y + height - a + 5,
                             arcade.color.BLACK)
        arcade.draw_text(str(self.vists[(shift+1)%3][(f[1]+1)%2]),
                             offset_x + p_width/2 + 5,
                             offset_y + height - a + 5,
                             arcade.color.BLACK)

        #E/S, E/N
        temp = str(self.vists[(shift+2)%3][f[2]])
        temp_offset = 10 + len(temp)*5
        arcade.draw_text(temp,
                             offset_x + width - temp_offset,
                             offset_y + 15,
                             arcade.color.BLACK,
                             rotation=90)
        temp = str(self.vists[(shift+2)%3][(f[2]+1)%2])
        temp_offset = 10 + len(temp)*5
        arcade.draw_text(temp,
                             offset_x + width - temp_offset,
                             offset_y + height/2 + 15,
                             arcade.color.BLACK,
                             rotation=90)

        #finish
        if self.finished:
            arcade.draw_text(str(self.final[shift]),
                             offset_x + p_width/2 - 100,
                             offset_y + b + 5,
                             arcade.color.RED)
            arcade.draw_text(str(self.final[(shift+1)%3]),
                             offset_x + p_width/2 - 100,
                             offset_y + height/2 + 5,
                             arcade.color.RED)
            temp = str(self.final[(shift+2)%3])
            temp_offset = 10 + len(temp)*5
            arcade.draw_text(temp,
                             offset_x + g_width - temp_offset,
                             offset_y + b + 75,
                             arcade.color.RED,
                             rotation = 90)


                    
