import pygame
from core.constants import Direction

import pygame
from core.constants import Direction

class TrafficLight:
    def __init__(self, is_five_way=False):
        self.is_five_way = is_five_way
        self.phase = "HORIZONTAL"  # HORIZONTAL, VERTICAL, DIAGONAL
        self.state = "GREEN"       # GREEN, YELLOW
        self.countdown = 4
        self.tick = 0
        self.manual_mode = False

    def update(self):
        if self.manual_mode:
            return
        
        self.tick += 1
        if self.tick >= 40:  # 40 ticks = 1 giây
            self.tick = 0
            self.countdown -= 1
            if self.countdown <= 0:
                self._switch_state()

    def change(self):
        if not self.manual_mode:
            return
        self._switch_state()

    def _switch_state(self):
        if self.state == "GREEN":
            self.state = "YELLOW"
            self.countdown = 2
        else:
            self.state = "GREEN"
            if self.is_five_way:
                if self.phase == "HORIZONTAL":
                    self.phase = "VERTICAL"
                elif self.phase == "VERTICAL":
                    self.phase = "DIAGONAL"
                else:
                    self.phase = "HORIZONTAL"
            else:
                self.phase = "VERTICAL" if self.phase == "HORIZONTAL" else "HORIZONTAL"
            self.countdown = 4

    def can_go(self, direction):
        if self.state != "GREEN":
            return False
        
        if self.is_five_way:
            if self.phase == "HORIZONTAL": return direction in [Direction.EAST, Direction.WEST]
            elif self.phase == "VERTICAL": return direction in [Direction.NORTH, Direction.SOUTH]
            elif self.phase == "DIAGONAL": return direction == Direction.SOUTHWEST
        else:
            if self.phase == "HORIZONTAL": return direction in [Direction.EAST, Direction.WEST]
            elif self.phase == "VERTICAL": return direction in [Direction.NORTH, Direction.SOUTH]
        return False

    def is_green_for(self, direction):
        return self.can_go(direction)

    def is_yellow_for(self, direction):
        if self.state != "YELLOW":
            return False
        if self.is_five_way:
            if self.phase == "HORIZONTAL": return direction in [Direction.EAST, Direction.WEST]
            elif self.phase == "VERTICAL": return direction in [Direction.NORTH, Direction.SOUTH]
            elif self.phase == "DIAGONAL": return direction == Direction.SOUTHWEST
        else:
            if self.phase == "HORIZONTAL": return direction in [Direction.EAST, Direction.WEST]
            elif self.phase == "VERTICAL": return direction in [Direction.NORTH, Direction.SOUTH]
        return False

    # ========================================================
    # THUẬT TOÁN MỚI: Tính chính xác thời gian chờ Đèn Đỏ
    # ========================================================
    def get_remaining_red_time(self, direction):
        if self.is_five_way:
            phases_order = ["HORIZONTAL", "VERTICAL", "DIAGONAL"]
        else:
            phases_order = ["HORIZONTAL", "VERTICAL"]

        # Xác định xem hướng của xe thuộc pha nào
        if direction in [Direction.EAST, Direction.WEST]:
            target_phase = "HORIZONTAL"
        elif direction in [Direction.NORTH, Direction.SOUTH]:
            target_phase = "VERTICAL"
        else:
            target_phase = "DIAGONAL"

        if self.phase == target_phase:
            return 0  # Đang không phải đèn đỏ

        current_idx = phases_order.index(self.phase)
        target_idx = phases_order.index(target_phase)

        # 1. Cộng thời gian đang chạy dở của pha hiện tại
        if self.state == "GREEN":
            time_left = self.countdown + 2  # Phải đợi hết Xanh + 2s Vàng
        else:
            time_left = self.countdown      # Chỉ đợi nốt Vàng

        # 2. Cộng dồn thời gian của các pha trung gian (Dành cho Ngã 5)
        idx = (current_idx + 1) % len(phases_order)
        while idx != target_idx:
            time_left += 6  # 4s Xanh + 2s Vàng của pha đứng giữa
            idx = (idx + 1) % len(phases_order)

        return time_left

    def draw_pole(self, surface, x, y, direction):
        width = 30
        height = 80
        
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height), border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2, border_radius=8)

        ball_d = 20
        ball_x = x + (width - ball_d) // 2
        red_y = y + 10
        yellow_y = y + 30
        green_y = y + 50

        is_green = self.is_green_for(direction)
        is_yellow = self.is_yellow_for(direction)
        is_red = not is_green and not is_yellow

        red_color = (255, 0, 0) if is_red else (80, 80, 80)
        yellow_color = (255, 255, 0) if is_yellow else (80, 80, 80)
        green_color = (0, 255, 0) if is_green else (80, 80, 80)

        pygame.draw.ellipse(surface, red_color, (ball_x, red_y, ball_d, ball_d))
        pygame.draw.ellipse(surface, yellow_color, (ball_x, yellow_y, ball_d, ball_d))
        pygame.draw.ellipse(surface, green_color, (ball_x, green_y, ball_d, ball_d))

        # Hiển thị số đếm ngược thực tế
        font = pygame.font.SysFont("Arial", 16, bold=True)
        
        if is_red:
            display_number = self.get_remaining_red_time(direction)
            text_color = (255, 0, 0)
        elif is_yellow:
            display_number = self.countdown
            text_color = (255, 255, 0)
        else:
            display_number = self.countdown
            text_color = (0, 255, 0)
            
        text = font.render(str(display_number), True, text_color)
        text_rect = text.get_rect(center=(x + width // 2, y - 12))
        
        pygame.draw.rect(surface, (0, 0, 0), text_rect.inflate(12, 6), border_radius=4)
        surface.blit(text, text_rect)

class Intersection:
    def __init__(self, x, y, inter_type, light):
        self.x = x
        self.y = y
        self.type = inter_type  # "3way", "4way", "5way"
        self.light = light