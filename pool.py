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

