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

class Point:
    def __init__(self, pos, size, color, name):
        self.id    = 0
        self.pos   = pos
        self.size  = size
        self.color = color
        self.name  = name
    
    def draw(self):
        pos = "x: " + str(self.pos.x) + " " + "y: " + str(self.pos.y)
        draw_circle(self.pos.x, self.pos.y, self.size, self.color)
        draw_text(self.name, self.pos.x - 5, self.pos.y - 5, 15, BLACK)
        draw_text(pos, self.pos.x + 25, self.pos.y + 10, 12, BLACK)

def bezier(p0, p1, p2, p3, t):
    a = vector2_lerp(p0, p1, t)
    b = vector2_lerp(p1, p2, t)
    c = vector2_lerp(p2, p3, t)   
    d = vector2_lerp(a, b, t)
    e = vector2_lerp(b, c, t)

    return vector2_lerp(d, e, t)

def draw_bezier(p0, p1, p2, p3):
    t = 0.0
    while t <= 1.0:
        point1 = bezier(p0.pos, p1.pos, p2.pos, p3.pos, t)
        t += 0.01
        point2 = bezier(p0.pos, p1.pos, p2.pos, p3.pos, t)
        draw_line_v(point1, point2, BLACK)
        t += 0.01

def draw_points(points):
    for i in range(0, 5):
        points[i].draw()
        next_index = (i + 1) % 5 # Wrap around to the first point for the last connection
        draw_line(points[i].pos.x, points[i].pos.y, points[next_index].pos.x, points[next_index].pos.y, GREEN)

def draw_button(text, button_rec):
    mouse_pos = get_mouse_position()
    is_mouse_over = check_collision_point_rec(mouse_pos, button_rec)

    text_x = button_rec.x + (button_rec.width - measure_text(text, 11)) / 2
    text_y = button_rec.y + (button_rec.height - 11) / 2

    rec_color = DARKBROWN if is_mouse_over else LIGHTGRAY
    text_color = BLACK if is_mouse_over else DARKGRAY

    draw_rectangle_rec(button_rec, rec_color)
    draw_text(text, text_x, text_y, 11, text_color)

    return is_mouse_over and is_mouse_button_pressed(MOUSE_LEFT_BUTTON)

def main():
    init_window(1080, 720, "Bézier curve")
    set_target_fps(120)

    camera = Camera2D()
    camera.target   = Vector2(0, 0)
    camera.offset   = Vector2(200.0, 200.0)
    camera.rotation = 0.0
    camera.zoom     = 1.0

    p0 = Point(Vector2(100, 200), int(20), GREEN, str("p0"))
    p1 = Point(Vector2(80,  100), int(20), GREEN, str("p1"))
    p2 = Point(Vector2(320, 100), int(20), GREEN, str("p2"))
    p3 = Point(Vector2(300, 200), int(20), GREEN, str("p3"))

    points = [p0, p0, p1, p2, p3]
    point_radius = float(0.0)

    is_dragging = False
    
    lock_id = int()

    for i in range(0, 5):
        points[i].id = i
    
    ball = Point(Vector2(100.0 * 1.5, 200.0 * 2.0), int(20), BLUE, str("Ball"))
    is_ball_pause = False
    is_ball_forward = True
    t = 0.0

    is_reset_ball = False
    is_reset_points = False

    while not window_should_close():
        delta_time = 0.3 * get_frame_time()      
        if not is_ball_pause:
            if is_ball_forward:
                if t < 1.0:
                    t += delta_time
                else:
                    t = 1.0
                    is_ball_forward = False
            else:
                if t > 0.0 and not is_ball_pause:
                    t -= delta_time
                else:
                    t = 0.0
                    is_ball_forward = True

        new_ball_pos = bezier(p0.pos, p1.pos, p2.pos, p3.pos, t)
        ball.pos = new_ball_pos

        if is_reset_ball:
            ball.pos = p0.pos
            t = 0.0

        mouse_pos = get_mouse_position()
        world_mouse_pos = get_screen_to_world2d(mouse_pos, camera)

        for point in points:
            if is_dragging:
                point_radius = point.size * 3.0
            else:
                point_radius = point.size

            if check_collision_point_circle(world_mouse_pos, point.pos, point_radius) and is_mouse_button_down(MOUSE_LEFT_BUTTON) and not is_dragging:
                lock_id = point.id
                if lock_id == point.id:
                    is_dragging = True
            
            elif is_mouse_button_released(MOUSE_LEFT_BUTTON):
                is_dragging = False
                lock_id = -1

            if is_dragging and point.id == lock_id:
                point.pos = world_mouse_pos

        if is_reset_points:
            p0.pos = Vector2(100, 200)
            p1.pos = Vector2(80,  100)
            p2.pos = Vector2(320, 100)
            p3.pos = Vector2(300, 200)

        begin_drawing()
        clear_background(RAYWHITE)

        begin_mode2d(camera)
        draw_points(points)
        draw_bezier(p0, p1, p2, p3)
        ball.draw()
        end_mode2d()

        is_reset_ball = draw_button("Reset Ball",   Rectangle(get_screen_width() - 120, 120, 100, 32))
        is_reset_points = draw_button("Reset Points", Rectangle(get_screen_width() - 120, 80, 100, 32))
        draw_text("Bézier curve", 20, 10, 24, BLACK)
        draw_text("by Wildan R Wijanarko", 45, 38, 12, BLACK)
        draw_fps(get_screen_width() - 80, 10)
        end_drawing()
        
    close_window()

if __name__ == '__main__':
    main()