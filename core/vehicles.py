import pygame
from core.constants import Direction
from core.strategies import NormalDriver, AggressiveDriver, EmergencyDriver

class Vehicle:
    def __init__(self, x, y, speed, direction, name, color, driver_strategy):
        self.x = x
        self.y = y
        self.original_speed = speed
        self.speed = speed
        self.direction = direction
        self.name = name
        self.color = color 
        self.driver = driver_strategy
        
        # Xác định tọa độ gốc để lúc vượt xe xong biết đường quay về làn cũ
        self.original_lane_pos = y if direction in [Direction.EAST, Direction.WEST] else x
        
        # Các cờ (flags) trạng thái (chuyển từ isYielding, isOvertaking... của Java)
        self.is_yielding = False
        self.is_overtaking = False
        
        # Các biến phục vụ logic rẽ ngã tư
        self.approaching_turn = False
        self.turn_center_x = 0
        self.turn_center_y = 0
        self.turn_new_dir = None
        self.snap_x = -1
        self.snap_y = -1
        self.has_decided_turn = False
        self.has_turned_ever = False
        self.enter_time = -1

    def move(self, light_allows, all_vehicles):
        # Tạm thời gọi chiến lược lái xe. 
        # Logic rẽ phức tạp (check va chạm khi rẽ) sẽ được tích hợp ở Controller sau.
        self.driver.move(self, light_allows)

    def update_position(self, actual_speed):
        if self.direction == Direction.EAST:
            self.x += actual_speed
        elif self.direction == Direction.WEST:
            self.x -= actual_speed
        elif self.direction == Direction.SOUTH:
            self.y += actual_speed
        elif self.direction == Direction.NORTH:
            self.y -= actual_speed
        elif self.direction == Direction.SOUTHWEST:
            self.x -= actual_speed
            self.y += actual_speed

    def reset_speed(self):
        self.speed = self.original_speed

    def get_body_width(self):
        return 55

    def get_body_height(self):
        return 32

    def get_priority_level(self):
        # Thay vì dùng instanceof như Java, Python dùng isinstance
        if isinstance(self, (Ambulance, FireTruck)):
            return 2
        return 1

    def draw_basic(self, surface):
        """Hàm vẽ xe bằng các khối cơ bản (Thay thế cho Graphics g trong Java)"""
        if self.direction in [Direction.EAST, Direction.WEST, Direction.SOUTHWEST]:
            w, h = 55, 32
        else:
            w, h = 32, 55
            
        # Vẽ hình chữ nhật đại diện cho xe
        pygame.draw.rect(surface, self.color, (self.x, self.y, w, h))
        
        # Vẽ tên xe (màu đen)
        font = pygame.font.SysFont("Arial", 12, bold=True)
        text = font.render(self.name, True, (0, 0, 0))
        surface.blit(text, (self.x + 5, self.y + 10))

# ==========================================
# CÁC LỚP KẾ THỪA (Tương tự extends trong Java)
# ==========================================

class Car(Vehicle):
    def __init__(self, x, y, direction):
        # Color: RGB(0, 0, 255) là màu Xanh lam
        super().__init__(x, y, 5, direction, "Car", (0, 0, 255), NormalDriver())

class Motorcycle(Vehicle):
    def __init__(self, x, y, direction):
        # Color: RGB(255, 0, 0) là màu Đỏ
        super().__init__(x, y, 9, direction, "Motor", (255, 0, 0), AggressiveDriver())

class Bicycle(Vehicle):
    def __init__(self, x, y, direction):
        # Color: RGB(0, 255, 0) là màu Xanh lá
        super().__init__(x, y, 3, direction, "Bike", (0, 255, 0), NormalDriver())

class Ambulance(Vehicle):
    def __init__(self, x, y, direction):
        # Color: RGB(255, 255, 255) là màu Trắng
        super().__init__(x, y, 8, direction, "Ambu", (255, 255, 255), EmergencyDriver())

class FireTruck(Vehicle):
    def __init__(self, x, y, direction):
        # Color: RGB(255, 165, 0) là màu Cam
        super().__init__(x, y, 7, direction, "Fire", (255, 165, 0), EmergencyDriver())