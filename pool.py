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

def write_pool(center_x, center_y, width, height,
               pool, hill, vists):
    offset_x = center_x - width/2
    offset_y = center_y - height/2
    a = height * (1/5)
    b = height/3
    p_width = width*(1-a/height)
    g_width = width*(1-b/height)

    #Names
    arcade.draw_text("S", center_x - 10,
                     center_y - 40,
                     arcade.color.BLACK,
                     font_size=24)
    arcade.draw_text("N", center_x - 10,
                     center_y + 15,
                     arcade.color.BLACK,
                     font_size=24)
    arcade.draw_text("E", center_x + 25,
                     center_y - 5,
                     arcade.color.BLACK,
                     font_size=24,
                     rotation=90)
    #Pool
    arcade.draw_text(str(pool[0]),offset_x + 5,
                             offset_y + a + 5,
                             arcade.color.BLACK)
    arcade.draw_text(str(pool[1]),offset_x + 5,
                             offset_y + height - b + 5,
                             arcade.color.BLACK)
        
    arcade.draw_text(str(pool[2]),offset_x + p_width - 15,
                             offset_y + a + 15,
                             arcade.color.BLACK,
                             rotation = 90)

    #Hill
    arcade.draw_text(str(hill[0]),offset_x + p_width/2 - 20,
                             offset_y + b + 5,
                             arcade.color.BLACK)
    arcade.draw_text(str(hill[1]),offset_x + p_width/2 - 20,
                             offset_y + height/2 + 5,
                             arcade.color.BLACK)
        
    arcade.draw_text(str(hill[2]),offset_x + g_width - 15,
                             offset_y + b + 15,
                             arcade.color.BLACK,
                             rotation = 90)

    #Vists
    #S/N, S/E
    arcade.draw_text(str(vists[0][0]),offset_x + 5,
                             offset_y + 5,
                             arcade.color.BLACK)
    arcade.draw_text(str(vists[0][1]),offset_x + p_width/2 + 5,
                             offset_y + 5,
                             arcade.color.BLACK)

    #N/S, N/E
    arcade.draw_text(str(vists[1][0]),offset_x + 5,
                             offset_y + height - a + 5,
                             arcade.color.BLACK)
    arcade.draw_text(str(vists[1][1]),offset_x + p_width/2 + 5,
                             offset_y + height - a + 5,
                             arcade.color.BLACK)

    #E/S, E/N
    arcade.draw_text(str(vists[2][0]),offset_x + width - 15,
                             offset_y + 15,
                             arcade.color.BLACK,
                             rotation=90)
    arcade.draw_text(str(vists[2][1]),offset_x + width - 15,
                             offset_y + height/2 + 15,
                             arcade.color.BLACK,
                             rotation=90)

def draw_star(x, y):
    point_list1 =((x-5,y),
                  (x,y+10),
                  (x+5,y),
                  (x,y-10))
    arcade.draw_polygon_filled(point_list1, 
                               arcade.color.YELLOW_ORANGE)
    point_list2 =((x-10,y),
                  (x,y+5),
                  (x+10,y),
                  (x,y-5))
    arcade.draw_polygon_filled(point_list2, 
                               arcade.color.YELLOW_ROSE)

def draw_star_new(x, y, color1, color2):
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
        if who_is_who[i] != "пас" and  who_is_who[i] != "вист" \
            and  who_is_who[i] != "свой":
            return i

def what_game(who_is_who, i):
    if who_is_who[i][0] == 1:
        return 10
    else:
        return who_is_who[i][0]         
                               
class Score:
    def __init__(self, max_pool):
        self.max_pool = max_pool
        self.otvet_vist = False
        #For pool writing:
        # Пуля: Юг, Север, Восток
        self.pool = [5,6,7]
        # Гора: Юг, Север, Восток
        self.hill = [20,20,20]
        # Висты: юг на север и т.д.
        #[[S/N,S/E],[N/S,N/E],[E/S,E/N]
        self.vists = [[10,20],[30,40],[50,60]]

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
                if self.pool[i] < self.max_pool - 10:
                    self.pool[i] += 10
                else:
                    my_part = self.max_pool - self.pool[i]
                    help_part = 10 - my_part
                    self.pool[i] += my_part
                    self.help_by_pool(help_part)
            else:
                self.hill[i] += num_of_tricks[i] * 10
        else: #reg
            pass #for now

    def help_by_pool(self, help_part):
        pass

    def help_by_hill(self, help_part):
        pass

    def write_pool(self, center_x, center_y, width, height, shift):
        offset_x = center_x - width/2
        offset_y = center_y - height/2
        a = height * (1/5)
        b = height/3
        p_width = width*(1-a/height)
        g_width = width*(1-b/height)

        #Names
        arcade.draw_text("S", center_x - 10,
                     center_y - 40,
                     arcade.color.BLACK,
                     font_size=24)
        arcade.draw_text("N", center_x - 10,
                     center_y + 15,
                     arcade.color.BLACK,
                     font_size=24)
        arcade.draw_text("E", center_x + 25,
                     center_y - 5,
                     arcade.color.BLACK,
                     font_size=24,
                     rotation=90)
        #Pool
        arcade.draw_text(str(self.pool[shift]),
                             offset_x + 5,
                             offset_y + a + 5,
                             arcade.color.BLACK)
        arcade.draw_text(str(self.pool[(shift+1)%3]),
                             offset_x + 5,
                             offset_y + height - b + 5,
                             arcade.color.BLACK)
        
        arcade.draw_text(str(self.pool[(shift+2)%3]),
                             offset_x + p_width - 15,
                             offset_y + a + 15,
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
        
        arcade.draw_text(str(self.hill[(shift+2)%3]),
                             offset_x + g_width - 15,
                             offset_y + b + 15,
                             arcade.color.BLACK,
                             rotation = 90)

        #Vists
        #S/N, S/E
        arcade.draw_text(str(self.vists[shift][0]),
                             offset_x + 5,
                             offset_y + 5,
                             arcade.color.BLACK)
        arcade.draw_text(str(self.vists[shift][1]),
                             offset_x + p_width/2 + 5,
                             offset_y + 5,
                             arcade.color.BLACK)

        #N/S, N/E
        arcade.draw_text(str(self.vists[(shift+1)%3][0]),
                             offset_x + 5,
                             offset_y + height - a + 5,
                             arcade.color.BLACK)
        arcade.draw_text(str(self.vists[(shift+1)%3][1]),
                             offset_x + p_width/2 + 5,
                             offset_y + height - a + 5,
                             arcade.color.BLACK)

        #E/S, E/N
        arcade.draw_text(str(self.vists[(shift+2)%3][0]),
                             offset_x + width - 15,
                             offset_y + 15,
                             arcade.color.BLACK,
                             rotation=90)
        arcade.draw_text(str(self.vists[(shift+2)%3][1]),
                             offset_x + width - 15,
                             offset_y + height/2 + 15,
                             arcade.color.BLACK,
                             rotation=90)
                    
