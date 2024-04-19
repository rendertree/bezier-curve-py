#   Copyright (c) 2024 Wildan R Wijanarko (@wildan9)
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

from raylibpy import *

g_should_close = False

class Point:
    def __init__(self, pos, size, color, name):
        self.id    = 0
        self.pos   = pos
        self.size  = size
        self.color = color
        self.name  = name
    
    def draw(self):
        pos = "x: " + str(round(self.pos.x, 2)) + " " + "y: " + str(round(self.pos.y, 2))
        draw_circle(self.pos.x, self.pos.y, self.size, self.color)
        draw_text(self.name, self.pos.x - 5, self.pos.y - 5, 15, BLACK)
        draw_text(pos, self.pos.x + 25, self.pos.y + 10, 12, BLACK)

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x + other.x, self.y + other.y)
        else:
            raise TypeError("Unsupported operand type for +: Vec2 and " + str(type(other)))

    def __sub__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x - other.x, self.y - other.y)
        else:
            raise TypeError("Unsupported operand type for -: Vec2 and " + str(type(other)))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vec2(self.x * other, self.y * other)
        else:
            raise TypeError("Unsupported operand type for *: Vec2 and " + str(type(other)))

    def rl_vec(self):
        return Vector2(self.x, self.y)

    def lerp(self, other, t):
        if isinstance(other, Vec2) and isinstance(t, (int, float)):
            return Vec2(
                self.x + (other.x - self.x) * t,
                self.y + (other.y - self.y) * t
            )
        else:
            raise TypeError("Unsupported operand types for lerp: Vec2, " + str(type(other)) + ", " + str(type(t)))
        
class Slider():
    def __init__(self, rec):
        self._is_dragging = False     
        self.rec = rec
        
    def draw(self, value):
        slider_value = value
        offset_x = 0

        mouse_pos = get_mouse_position()

        if self._is_dragging:
            slider_value = (mouse_pos.x - self.rec.x - offset_x) / self.rec.width
            slider_value = max(0.0, min(1.0, slider_value))

        if check_collision_point_rec(mouse_pos, self.rec) and is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
            self._is_dragging = True
            offset_x = mouse_pos.x - self.rec.x - (slider_value * self.rec.width)

        if is_mouse_button_released(MOUSE_LEFT_BUTTON):
            self._is_dragging = False
            
        draw_rectangle_rec(self.rec, LIGHTGRAY)
        draw_rectangle(self.rec.x + int(slider_value * self.rec.width) - 10, self.rec.y, 20, self.rec.height, DARKPURPLE)
    
        return slider_value

class RLCamera(Camera2D):
    def __init__(self):
        self.target   = Vec2(0, 0).rl_vec()
        self.offset   = Vec2(200.0, 200.0).rl_vec()
        self.rotation = 0.0
        self.zoom     = 1.0

    def begin_mode(self):
        begin_mode2d(self)

    def end_mode(self):
        end_mode2d()

        return self

    def update(self, target):
        self.target = target

        if get_mouse_wheel_move() > 0.0 and self.zoom < 3.0:
            self.zoom += 0.1
        if get_mouse_wheel_move() < 0.0 and self.zoom > 0.0:
            self.zoom -= 0.1

class Dropdown():
    def __init__(self, title_text, text_arr, item_num, rec):
        self.title_text     = title_text
        self.text_arr       = text_arr
        self.item_num       = item_num
        self.rec            = rec
        self.current_item   = 0
        self._flag          = False
        self._str_mode      = "Select Mode"

    def draw(self):
        mouse_pos = get_mouse_position()
        
        draw_text(self.title_text, self.rec.x, self.rec.y - 14, 12, BLACK)

        if self._flag:
            for i in range(0, self.item_num):
                draw_button(self._str_mode, Rectangle(self.rec.x, self.rec.y, self.rec.width, self.rec.height))
                draw_rectangle_lines_ex(Rectangle(self.rec.x, self.rec.y, self.rec.width, self.rec.height), 1, BLACK)
                draw_button(self.text_arr[i], Rectangle(self.rec.x, self.rec.y + 35 * (i + 1), self.rec.width, self.rec.height))
                draw_rectangle_lines_ex(Rectangle(self.rec.x, self.rec.y + 35 * (i + 1), self.rec.width, self.rec.height), 1, BLACK)

                if check_collision_point_rec(mouse_pos, Rectangle(self.rec.x, self.rec.y + 35 * (i + 1), self.rec.width, self.rec.height)) and is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
                    self.current_item = i
                    self._str_mode = self.text_arr[i]
        else:
            draw_button(self._str_mode, Rectangle(self.rec.x, self.rec.y, self.rec.width, self.rec.height))
            draw_rectangle_lines_ex(Rectangle(self.rec.x, self.rec.y, self.rec.width, self.rec.height), 1, BLACK)

        if check_collision_point_rec(mouse_pos, self.rec) and is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
            self._flag = not self._flag
        elif is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and self._flag:
            self._flag = not self._flag

        return self.current_item

class MenuBar():
    def __init__(self):
        self._flag_file             = False
        self._flag_settings         = False
        self._flag_view             = False
        self._file_rec              = Rectangle(0, 0, 50, 30)
        self._settings_rec          = Rectangle(50, 0, 50, 30)
        self._view_rec              = Rectangle(100, 0, 50, 30)
        self._file_item_num         = 2
        self._settings_item_num     = 2
        self._view_item_num         = 2
        self._file_str_item         = ["Export to PNG", "Exit"]
        self._settings_str_item     = ["aa2", "bb2"]
        self._view_str_item         = ["Windowed", "Fullscreen"]
        self._file_btn_on_press     = False
        self._settings_btn_on_press = False
        self._view_btn_on_press     = False
        self._is_fullscreen         = False
        
        # Only for some buttons
        self._view_btn_state = [False, True]

    def draw(self):
        global g_should_close
        mouse_pos = get_mouse_position()

        #----------------------------------------------------------------
        # Draw the background
        bg_pos = Vec2(0, 0)
        bg_size = Vec2(get_screen_width(), 30)
        draw_rectangle_v(bg_pos.rl_vec(), bg_size.rl_vec(), LIGHTGRAY)

        #----------------------------------------------------------------
        # Draw the buttons
        
        # File
        draw_button("File", self._file_rec)
        if self._flag_file:
            for i in range(0, self._file_item_num):
                self._file_btn_on_press = draw_button(self._file_str_item[i], Rectangle(self._file_rec.x, self._file_rec.y + 30 * (i + 1), self._file_rec.width + 50, self._file_rec.height))

                if self._file_btn_on_press and i == 0:
                    take_screenshot("screenshot.png")

                if self._file_btn_on_press and i == 1:
                    g_should_close = True

        if check_collision_point_rec(mouse_pos, self._file_rec) and is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
            self._flag_file = not self._flag_file
        elif is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and self._flag_file:
            self._flag_file = not self._flag_file

        # Settings
        draw_button("Settings", self._settings_rec)
        if self._flag_settings:
            for i in range(0, self._settings_item_num):
                draw_button(self._settings_str_item[i], Rectangle(self._settings_rec.x, self._settings_rec.y + 30 * (i + 1), self._settings_rec.width + 50, self._settings_rec.height))

        if check_collision_point_rec(mouse_pos, self._settings_rec) and is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
            self._flag_settings = not self._flag_settings
        elif is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and self._flag_settings:
            self._flag_settings = not self._flag_settings

        # View
        draw_button("View", self._view_rec)
        if self._flag_view:
            for i in range(0, self._view_item_num):
                self._view_btn_on_press = draw_button(self._view_str_item[i], Rectangle(self._view_rec.x, self._view_rec.y + 30 * (i + 1), self._view_rec.width + 50, self._view_rec.height), self._view_btn_state[i])
                
                if self._view_btn_on_press and i == 0:
                    self._view_btn_state[0] = False
                    self._view_btn_state[1] = True
                    toggle_fullscreen()

                if self._view_btn_on_press and i == 1:
                    self._view_btn_state[0] = True
                    self._view_btn_state[1] = False
                    toggle_fullscreen()

        if check_collision_point_rec(mouse_pos, self._view_rec) and is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
            self._flag_view = not self._flag_view
        elif is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and self._flag_view:
            self._flag_view = not self._flag_view

class BezierObject(object):
    def __init__(self):
        self._p0 = Point(Vec2(100, 200), int(20), LIME, str("P0"))
        self._p1 = Point(Vec2(80,  100), int(20), LIME, str("P1"))
        self._p2 = Point(Vec2(320, 100), int(20), LIME, str("P2"))
        self._p3 = Point(Vec2(300, 200), int(20), LIME, str("P3"))
        self._points = [self._p0, self._p0, self._p1, self._p2, self._p3]
        self._point_radius = float(0.0)

        self._is_dragging = False
        
        self._lock_id = int()

        for i in range(0, 5):
            self._points[i].id = i

        self._ball = Point(Vec2(100.0 * 1.5, 200.0 * 2.0), int(12), BLUE, str("Ball"))
        self._is_ball_pause = False
        self._is_ball_manual_mode = False
        self._is_ball_forward = True

        self._is_reset_ball = False
        self._is_reset_points = False

        self._is_draw_abcde = True
        self._is_draw_abcde_line = True

        # In a Bézier curve, "t" represents a parameter that varies between 0.0 and 1.0, determining a point along the curve   
        self._t = 0.0
        self._at = 0.0 # Automatic "t"
        self._mt = 0.0 # Manual "t"

        self._slider_mt_pos = Vec2(50, get_screen_height() / 2)
        self._slider_mt = Slider(Rectangle(self._slider_mt_pos.x, self._slider_mt_pos.y, 150, 30))

        # Objects colors
        self._colors = [BLACK, RED, GREEN, BLUE, YELLOW, BROWN, LIME, PINK, PURPLE, GOLD, DARKBLUE, DARKPURPLE, DARKGRAY]
        self._ball_color = BLUE
        self._points_color = LIME
        self._abcde_color = PINK
        self._points_lines_color_0 = GOLD
        self._points_lines_color_1 = RED
        self._abcde_lines_color = PURPLE
        self._abcde_lines_color = BLACK
        self._is_generate_colors = False
        self._colors_length = 12
        self._is_blinking_mode = False
        self._current_blinking_mode = 0
        self._color_timer = 0.0
        self._color_update_time = 0.084
        self._objects_colors_mode_dropdown = Dropdown("Random Colors Mode", ["Mode 1", "Mode 2"], 2, Rectangle(140, 30, 100, 35))

        # Grid
        self._is_draw_grid = False

        # Menu bar
        self._menu_bar = MenuBar()

    def _bezier(self, p0, p1, p2, p3, t) -> Vec2:
        a = p0.lerp(p1, t)
        b = p1.lerp(p2, t)
        c = p2.lerp(p3, t)
        d = a.lerp(b, t)
        e = b.lerp(c, t)

        result = d.lerp(e, t)

        return result

    def _draw_bezier(self, p0, p1, p2, p3):
        t = 0.0
        while t <= 1.0:
            start_pos = self._bezier(p0.pos, p1.pos, p2.pos, p3.pos, t)
            t += 0.01
            end_pos = self._bezier(p0.pos, p1.pos, p2.pos, p3.pos, t)
            draw_line_v(start_pos.rl_vec(), end_pos.rl_vec(), BLACK)
            t += 0.01

    def _draw_points(self, points, points_color, lines_color_0, lines_color_1, t):
        for i in range(0, 5):
            points[i].color = points_color
            points[i].draw()
            next_index = (i + 1) % 5 # Wrap around to the first point for the last connection

            start_x = points[i].pos.x
            start_y = points[i].pos.y
            
            end_x = points[next_index].pos.x
            end_y = points[next_index].pos.y

            dx = start_x + (end_x - start_x) * t
            dy = start_y + (end_y - start_y) * t

            start_pos = Vec2(start_x, start_y)
            end_pos   = Vec2(end_x, end_y)

            if lines_color_0 == lines_color_1:
                self._points_lines_color_0 = self._colors[get_random_value(0, self._colors_length)]
                self._points_lines_color_1 = self._colors[get_random_value(0, self._colors_length)]
            
            draw_line_ex(start_pos.rl_vec(), end_pos.rl_vec(), 7.0, lines_color_0)
            draw_line_ex(start_pos.rl_vec(), Vec2(dx, dy).rl_vec(), 0.9, lines_color_1)

    def update(self, camera):
        def _get_random_color(self) -> Color: return self._colors[get_random_value(0, self._colors_length)]
        def _generate_colors(self):
            self._ball_color           = _get_random_color(self)
            self._points_color         = _get_random_color(self)
            self._abcde_color          = _get_random_color(self)
            self._points_lines_color_0 = _get_random_color(self)
            self._points_lines_color_1 = _get_random_color(self)
            self._abcde_lines_color    = _get_random_color(self)
        #----------------------------------------------------------------
        # Generate colors
        if self._is_generate_colors or self._is_blinking_mode:
            if self._is_blinking_mode:
                if self._current_blinking_mode == 0:
                    self._color_timer += get_frame_time() * 0.5
                    if self._color_timer >= self._color_update_time:
                        self._color_timer = 0.0
                        _generate_colors(self)
                elif self._current_blinking_mode == 1:
                    if self._t == 1.0 or self._t == 0.0: _generate_colors(self)
            else: _generate_colors(self)

        #----------------------------------------------------------------
        # Pause button
        if is_key_pressed(KEY_P):
            self._is_ball_pause = not self._is_ball_pause

        #----------------------------------------------------------------
        # Update the "t"
        delta_time = 0.3 * get_frame_time()      
        if not self._is_ball_pause and not self._is_ball_manual_mode:
            self._mt = self._t
            if self._is_ball_forward:
                if self._at < 1.0:
                    self._at += delta_time
                else:
                    self._at = 1.0
                    self._is_ball_forward = False
            else:
                if self._at > 0.0 and not self._is_ball_pause:
                    self._at -= delta_time
                else:
                    self._at = 0.0
                    self._is_ball_forward = True

        if self._is_ball_manual_mode:
            self._t = self._mt
        else:
            self._t = self._at

        #----------------------------------------------------------------
        # Update the ball position and color
        new_ball_pos = self._bezier(self._p0.pos, self._p1.pos, self._p2.pos, self._p3.pos, self._t)
        self._ball.pos = new_ball_pos

        if self._is_reset_ball:
            self._ball.pos = self._p0.pos
            self._t = 0.0

        self._ball.color = self._ball_color

        #----------------------------------------------------------------
        # Update the points position
        mouse_pos = get_mouse_position()
        world_mouse_pos = get_screen_to_world2d(mouse_pos, camera)

        for point in self._points:
            if self._is_dragging:
                self._point_radius = point.size * 3.0
            else:
                self._point_radius = point.size

            if check_collision_point_circle(world_mouse_pos, point.pos.rl_vec(), self._point_radius) and is_mouse_button_down(MOUSE_LEFT_BUTTON) and not self._is_dragging:
                self._lock_id = point.id
                if self._lock_id == point.id:
                    self._is_dragging = True
            
            elif is_mouse_button_released(MOUSE_LEFT_BUTTON):
                self._is_dragging = False
                self._lock_id = -1

            if self._is_dragging and point.id == self._lock_id:
                point.pos.x = world_mouse_pos.x
                point.pos.y = world_mouse_pos.y

        if self._is_reset_points:
            self._p0.pos = Vec2(100, 200)
            self._p1.pos = Vec2(80,  100)
            self._p2.pos = Vec2(320, 100)
            self._p3.pos = Vec2(300, 200)

    def draw_object(self):
        #----------------------------------------------------------------
        # Draw the control points
        self._draw_points(
            self._points, 
            self._points_color, 
            self._points_lines_color_0, 
            self._points_lines_color_1, 
            self._t)
        
        #----------------------------------------------------------------
        # Draw the bezier line
        self._draw_bezier(self._p0, self._p1, self._p2, self._p3)

        #----------------------------------------------------------------
        # Draw the ball
        self._ball.draw()

        # Update abcd points position
        a = self._p0.pos.lerp(self._p1.pos, self._t)
        b = self._p1.pos.lerp(self._p2.pos, self._t)
        c = self._p2.pos.lerp(self._p3.pos, self._t)
        d = a.lerp(b, self._t)
        e = b.lerp(c, self._t)

        #----------------------------------------------------------------
        # Draw the abcde points
        if self._is_draw_abcde:
            draw_circle(a.x, a.y, 7, self._abcde_color)
            draw_circle(b.x, b.y, 7, self._abcde_color)
            draw_circle(c.x, c.y, 7, self._abcde_color)
            draw_circle(d.x, d.y, 7, self._abcde_color)
            draw_circle(e.x, e.y, 7, self._abcde_color)

            draw_text("A", a.x, a.y, 14, BLACK)
            draw_text("B", b.x, b.y, 14, BLACK)
            draw_text("C", c.x, c.y, 14, BLACK)
            draw_text("D", d.x, d.y, 14, BLACK)
            draw_text("E", e.x, e.y, 14, BLACK)
            
            if self._is_draw_abcde_line: 
                draw_line_v(a.rl_vec(), b.rl_vec(), self._abcde_lines_color)
                draw_line_v(b.rl_vec(), c.rl_vec(), self._abcde_lines_color)
                draw_line_v(d.rl_vec(), e.rl_vec(), self._abcde_lines_color)

    def draw_gui(self):
        #----------------------------------------------------------------
        # Draw the buttons
        self._is_generate_colors = draw_button("Generate Colors",     Rectangle(get_screen_width() - 120, 80 + 40 * 0, 100, 32))
        self._is_reset_points = draw_button("Reset Points",           Rectangle(get_screen_width() - 120, 80 + 40 * 1, 100, 32))
        self._is_reset_ball = draw_button("Reset Ball",               Rectangle(get_screen_width() - 120, 80 + 40 * 2, 100, 32))

        #----------------------------------------------------------------
        # Draw the checkboxes
        self._is_ball_manual_mode = draw_checkbox("Manual Mode",      Rectangle(10, 90 + 40 * 0, 32, 32), self._is_ball_manual_mode)
        self._is_draw_abcde = draw_checkbox("Draw abcde",             Rectangle(10, 90 + 40 * 1, 32, 32), self._is_draw_abcde)
        self._is_draw_abcde_line = draw_checkbox("Draw abcde line",   Rectangle(10, 90 + 40 * 2, 32, 32), self._is_draw_abcde_line)
        self._is_ball_pause = draw_checkbox("Pause",                  Rectangle(10, 90 + 40 * 3, 32, 32), self._is_ball_pause)
        self._is_blinking_mode = draw_checkbox("Blinking Mode",       Rectangle(10, 90 + 40 * 4, 32, 32), self._is_blinking_mode)

        #----------------------------------------------------------------
        # Draw the slider
        draw_text("MT Slider: ", self._slider_mt_pos.x, self._slider_mt_pos.y - 16, 18, BLACK)
        self._mt = self._slider_mt.draw(self._mt)

        #----------------------------------------------------------------
        # Draw the dropdown
        if self._is_blinking_mode:
            self._current_blinking_mode = self._objects_colors_mode_dropdown.draw()
        
        if self._is_ball_pause:
            draw_text("Paused", get_screen_width() / 2 - 100, 50, 44, RED)

def draw_button(text, button_rec, is_clickable=True):
        mouse_pos = get_mouse_position()
        is_mouse_over = check_collision_point_rec(mouse_pos, button_rec)

        text_x = button_rec.x + (button_rec.width - measure_text(text, 11)) / 2
        text_y = button_rec.y + (button_rec.height - 11) / 2

        rec_color = DARKBROWN if is_mouse_over else LIGHTGRAY
        
        text_color = BLACK
        if is_clickable:
            text_color = BLACK if is_mouse_over else DARKGRAY
        else:
            text_color = GRAY

        draw_rectangle_rec(button_rec, rec_color)
        draw_text(text, text_x, text_y, 11, text_color)

        return is_clickable and is_mouse_over and is_mouse_button_pressed(MOUSE_LEFT_BUTTON)

def draw_checkbox(text, rec, flag):
    mouse_pos = get_mouse_position()
    is_mouse_over = check_collision_point_rec(mouse_pos, rec)

    if flag:
        draw_rectangle_rec(rec, DARKBLUE)

    draw_rectangle_lines_ex(rec, 4, BLACK)
    draw_text(text, rec.x + 35, rec.y + 20, 12, BLACK)

    if is_mouse_over and is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
        flag = not flag

    return flag

class app():
    def __init__(self):
        self.screen_width    = 1080
        self.screen_height   = 720
        self.world_width     = 2200
        self.world_height    = 2200
        self.grid_size       = 80

        set_config_flags(FLAG_MSAA_4X_HINT)
        init_window(self.screen_width, self.screen_height, "Bézier curve")
        set_target_fps(120)

        self.camera = RLCamera()
    
        # Grid
        self.is_draw_grid = False

        # Menu bar
        self.menu_bar = MenuBar()

        # Bezier object
        self.bezier_object = BezierObject()
    
    def _draw_grid(self):
        if self.is_draw_grid:
            for x in range(-self.world_width // 2, (self.world_width // 2) + 1, self.grid_size):
                draw_line(x, -self.world_height // 2, x, self.world_height // 2, DARKGRAY)

            for y in range(-self.world_height // 2, (self.world_height // 2) + 1, self.grid_size):
                draw_line(-self.world_width // 2, y, self.world_width // 2, y, DARKGRAY)

    def _draw_gui0(self):
        #----------------------------------------------------------------
        # Draw grid
        self._draw_grid()
    
    def _draw_gui1(self):
        #----------------------------------------------------------------
        # Draw the bezier GUI
        self.bezier_object.draw_gui()
        
        #----------------------------------------------------------------
        # Draw the menu bar
        self.menu_bar.draw()

        #----------------------------------------------------------------
        # Grid checkbox
        self.is_draw_grid = draw_checkbox("Draw Grid", Rectangle(10, 90 + 40 * 5, 32, 32), self.is_draw_grid)

        #----------------------------------------------------------------
        # Draw additional text
        draw_text("Bézier curve", self.screen_width - 220, self.screen_height - 80, 24, BLACK)
        draw_text("by Wildan R Wijanarko",  self.screen_width - 200, self.screen_height - 50, 12, BLACK)
        draw_fps(self.screen_width - 80, 10)

    def update(self):
        self.bezier_object.update(self.camera)

    def render(self):
        begin_drawing()
        clear_background(RAYWHITE)

        self._draw_gui0()

        self.camera.begin_mode()

        #----------------------------------------------------------------
        # Draw the bezier object
        self.bezier_object.draw_object()
        
        self.camera.end_mode()
    
        self._draw_gui1()

        end_drawing()

    def shutdown(self):
        close_window()

if __name__ == '__main__':
    _app_ = app()
    
    while not window_should_close() and not g_should_close:
        _app_.update()
        _app_.render()

    _app_.shutdown()
