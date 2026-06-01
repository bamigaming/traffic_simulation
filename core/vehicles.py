import pygame
import random
from core.constants import Direction

class Vehicle:
    def __init__(self, x, y, direction, name, color, speed):
        self.x = x
        self.y = y
        self.direction = direction
        self.name = name
        self.color = color
        self.speed = speed
        
        self.turn_intent = random.choices(["STRAIGHT", "RIGHT", "LEFT", "DIAGONAL"], weights=[50, 15, 15, 20])[0]
        self.has_turned = False 

        # Kích thước thật của xe: Dài 55, Rộng 32
        self.length = 55
        self.width = 32

    def get_body_width(self):
        # Trả về Hitbox AABB để tính toán Radar
        if self.direction in [Direction.EAST, Direction.WEST]: return self.length
        if self.direction in [Direction.NORTH, Direction.SOUTH]: return self.width
        return 45 

    def get_body_height(self):
        if self.direction in [Direction.EAST, Direction.WEST]: return self.width
        if self.direction in [Direction.NORTH, Direction.SOUTH]: return self.length
        return 45

    def move(self, is_allowed, all_vehicles):
        if not is_allowed: return
        
        if self.direction == Direction.EAST: self.x += self.speed
        elif self.direction == Direction.WEST: self.x -= self.speed
        elif self.direction == Direction.SOUTH: self.y += self.speed
        elif self.direction == Direction.NORTH: self.y -= self.speed
        elif self.direction == Direction.NORTHEAST:
            self.x += self.speed * 0.707
            self.y -= self.speed * 0.707
        elif self.direction == Direction.SOUTHWEST:
            self.x -= self.speed * 0.707
            self.y += self.speed * 0.707

    def draw_basic(self, surface):
        # 1. Vẽ xe trên một mặt phẳng trung gian trong suốt (Mặc định hướng ĐÔNG)
        veh_surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        pygame.draw.rect(veh_surface, self.color, (0, 0, self.length, self.width), border_radius=8)
        pygame.draw.rect(veh_surface, (0, 0, 0), (0, 0, self.length, self.width), 2, border_radius=8)

        if self.name in ["Ambu", "Fire"]:
            pygame.draw.circle(veh_surface, (255, 255, 0), (self.length // 2, self.width // 2), 5)

        font = pygame.font.SysFont("Arial", 10, bold=True)
        text_color = (255, 255, 255) if self.name in ["Car", "Motor"] else (0, 0, 0)
        text = font.render(self.name, True, text_color)
        text_rect = text.get_rect(center=(self.length // 2, self.width // 2))
        veh_surface.blit(text, text_rect)

        # 2. Quay xe theo hướng di chuyển bằng Transform
        angle = 0
        if self.direction == Direction.NORTH: angle = 90
        elif self.direction == Direction.WEST: angle = 180
        elif self.direction == Direction.SOUTH: angle = 270
        elif self.direction == Direction.NORTHEAST: angle = 45
        elif self.direction == Direction.SOUTHWEST: angle = 225

        rotated_surface = pygame.transform.rotate(veh_surface, angle)
        
        # 3. Canh tâm để hình ảnh không bị giật / lắc khi xoay
        center_x = self.x + self.get_body_width() // 2
        center_y = self.y + self.get_body_height() // 2
        rect = rotated_surface.get_rect(center=(center_x, center_y))
        
        surface.blit(rotated_surface, rect.topleft)

class Car(Vehicle):
    def __init__(self, x, y, dir): super().__init__(x, y, dir, "Car", (0, 0, 255), 5)
class Motorcycle(Vehicle):
    def __init__(self, x, y, dir): super().__init__(x, y, dir, "Motor", (255, 0, 0), 6)
class Bicycle(Vehicle):
    def __init__(self, x, y, dir): super().__init__(x, y, dir, "Bike", (0, 255, 0), 3)
class Ambulance(Vehicle):
    def __init__(self, x, y, dir): super().__init__(x, y, dir, "Ambu", (255, 255, 255), 7)
class FireTruck(Vehicle):
    def __init__(self, x, y, dir): super().__init__(x, y, dir, "Fire", (255, 165, 0), 7)