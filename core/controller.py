import random
import pygame 
import math
from core.constants import Direction
from core.vehicles import Car, Motorcycle, Bicycle, Ambulance, FireTruck

class TrafficController:
    def __init__(self, intersections, vehicles):
        self.intersections = intersections
        self.vehicles = vehicles
        self.WIDTH, self.HEIGHT = 1600, 900
        self.ROAD_WIDTH = 240
        self.ROAD_START_Y = 220
        self.MAX_CAPACITY = 40
        
        self.WEST_LANE_SLOW = 224; self.WEST_LANE_FAST = 264; self.WEST_LANE_EMG = 304
        self.EAST_LANE_EMG = 344; self.EAST_LANE_FAST = 384; self.EAST_LANE_SLOW = 424

        self.ticks = 0
        self.lane_change_cooldown = {}

    def can_change_lane(self, v):
        last_change = self.lane_change_cooldown.get(id(v), -999)
        return (self.ticks - last_change) > 15

    def spawn_vehicle(self):
        if len(self.vehicles) >= self.MAX_CAPACITY: return 
        vehicle_types = [Car, Car, Car, Motorcycle, Bicycle, Ambulance, FireTruck]
        VehicleClass = random.choice(vehicle_types)
        
        inter5 = next((i for i in self.intersections if i.type == "5way"), None)
        if inter5 and random.random() < 0.20:
            cx5 = inter5.x + self.ROAD_WIDTH // 2
            cy5 = self.ROAD_START_Y + self.ROAD_WIDTH // 2
            spawn_x = self.WIDTH + 60
            spawn_y = cy5 - (spawn_x - cx5) + 30 
            direction = Direction.SOUTHWEST
            for v in self.vehicles:
                if v.direction == direction and math.hypot(v.x - spawn_x, v.y - spawn_y) < 160: return 
            new_v = VehicleClass(spawn_x, spawn_y, direction)
            new_v.turn_intent = "STRAIGHT" 
            self.vehicles.append(new_v)
            return

        is_east = random.choice([True, False])
        direction = Direction.EAST if is_east else Direction.WEST
        spawn_x = -60 if is_east else self.WIDTH + 60
        possible_lanes = []
        if is_east:
            if VehicleClass in [Ambulance, FireTruck]: possible_lanes = [self.EAST_LANE_SLOW, self.EAST_LANE_FAST, self.EAST_LANE_EMG]
            elif VehicleClass == Car: possible_lanes = [self.EAST_LANE_SLOW, self.EAST_LANE_FAST]
            else: possible_lanes = [self.EAST_LANE_SLOW]
        else:
            if VehicleClass in [Ambulance, FireTruck]: possible_lanes = [self.WEST_LANE_SLOW, self.WEST_LANE_FAST, self.WEST_LANE_EMG]
            elif VehicleClass == Car: possible_lanes = [self.WEST_LANE_SLOW, self.WEST_LANE_FAST]
            else: possible_lanes = [self.WEST_LANE_SLOW]
                
        spawn_y = random.choice(possible_lanes)
        for v in self.vehicles:
            if v.direction == direction and v.y == spawn_y and abs(v.x - spawn_x) < 160: return 
        self.vehicles.append(VehicleClass(spawn_x, spawn_y, direction))

    def _is_spot_occupied(self, v, target_x, target_y):
        """Hàm quét Radar thông minh: Check xem chỗ định rẽ tới có xe không"""
        test_rect = pygame.Rect(target_x, target_y, 45, 45)
        for o in self.vehicles:
            if o != v:
                o_rect = pygame.Rect(o.x, o.y, o.get_body_width(), o.get_body_height())
                if test_rect.colliderect(o_rect): return True
        return False

    def execute_turn(self, v):
        for inter in self.intersections:
            if inter.type == "5way":
                cx = inter.x + self.ROAD_WIDTH // 2
                cy = self.ROAD_START_Y + self.ROAD_WIDTH // 2
                
                # Rẽ vào làn chéo
                if v.direction == Direction.EAST and v.turn_intent == "DIAGONAL" and not v.has_turned:
                    if abs(v.x - (cx - 30)) <= v.speed * 2:
                        target_x, target_y = cx - 20, cy - 20
                        if not self._is_spot_occupied(v, target_x, target_y):
                            v.x, v.y, v.direction, v.has_turned = target_x, target_y, Direction.NORTHEAST, True
                        return

                # Từ làn chéo nhập xuống đường thẳng
                if v.direction == Direction.SOUTHWEST and not v.has_turned:
                    if abs(v.x - (cx + 30)) <= v.speed * 2:
                        next_dir = random.choice([Direction.WEST, Direction.SOUTH])
                        if next_dir == Direction.WEST:
                            target_x, target_y = cx - 40, self.WEST_LANE_FAST
                        else:
                            target_x, target_y = inter.x + 64, cy + 40
                            
                        if not self._is_spot_occupied(v, target_x, target_y):
                            v.x, v.y, v.direction, v.has_turned = target_x, target_y, next_dir, True
                        return

            if v.turn_intent == "STRAIGHT" or v.has_turned: continue
            if inter.type == "3way" and v.turn_intent == "LEFT" and v.direction == Direction.EAST: continue
            if inter.type == "3way" and v.turn_intent == "RIGHT" and v.direction == Direction.WEST: continue

            SOUTH_LANES = [inter.x + 24, inter.x + 64, inter.x + 104] 
            NORTH_LANES = [inter.x + 216, inter.x + 176, inter.x + 136]
            target_x, target_dir = None, None

            if v.direction == Direction.EAST:
                if v.turn_intent == "RIGHT": target_x, target_dir = (SOUTH_LANES[1] if v.name != "Bike" else SOUTH_LANES[0]), Direction.SOUTH
                elif v.turn_intent == "LEFT": target_x, target_dir = (NORTH_LANES[1] if v.name != "Bike" else NORTH_LANES[0]), Direction.NORTH
            elif v.direction == Direction.WEST:
                if v.turn_intent == "RIGHT": target_x, target_dir = (NORTH_LANES[1] if v.name != "Bike" else NORTH_LANES[0]), Direction.NORTH
                elif v.turn_intent == "LEFT": target_x, target_dir = (SOUTH_LANES[1] if v.name != "Bike" else SOUTH_LANES[0]), Direction.SOUTH

            if target_x and target_dir:
                if abs(v.x - target_x) <= v.speed:
                    if not self._is_spot_occupied(v, target_x, v.y):
                        v.x, v.direction, v.has_turned = target_x, target_dir, True

    def check_safe_distance(self, current_v, threshold=35):
        """Thuật toán Radar Vector chống Deadlock (Kẹt chết)"""
        cw, ch = current_v.get_body_width(), current_v.get_body_height()
        offset = 6 
        
        # Hộp dự đoán vươn về phía trước
        if current_v.direction == Direction.EAST: pred_rect = pygame.Rect(current_v.x, current_v.y + offset, cw + threshold, ch - offset*2)
        elif current_v.direction == Direction.WEST: pred_rect = pygame.Rect(current_v.x - threshold, current_v.y + offset, cw + threshold, ch - offset*2)
        elif current_v.direction == Direction.SOUTH: pred_rect = pygame.Rect(current_v.x + offset, current_v.y, cw - offset*2, ch + threshold)
        elif current_v.direction == Direction.NORTH: pred_rect = pygame.Rect(current_v.x + offset, current_v.y - threshold, cw - offset*2, ch + threshold)
        elif current_v.direction == Direction.NORTHEAST: pred_rect = pygame.Rect(current_v.x + offset, current_v.y - threshold, cw + threshold, ch + threshold)
        elif current_v.direction == Direction.SOUTHWEST: pred_rect = pygame.Rect(current_v.x - threshold, current_v.y + offset, cw + threshold, ch + threshold)
        else: pred_rect = pygame.Rect(current_v.x, current_v.y, cw, ch)

        my_cx = current_v.x + cw / 2
        my_cy = current_v.y + ch / 2

        for other in self.vehicles:
            if other == current_v: continue
            
            # Thu nhỏ hitbox đối phương 4px để không bị kẹt khi đi sượt ngang sườn
            shrink = 4
            ow, oh = other.get_body_width(), other.get_body_height()
            other_rect = pygame.Rect(other.x + shrink, other.y + shrink, ow - shrink*2, oh - shrink*2)
            
            if pred_rect.colliderect(other_rect):
                other_cx = other.x + ow / 2
                other_cy = other.y + oh / 2
                
                # Tính Vector tương đối
                dx = other_cx - my_cx
                dy = other_cy - my_cy
                
                vx, vy = 0, 0
                if current_v.direction == Direction.EAST: vx, vy = 1, 0
                elif current_v.direction == Direction.WEST: vx, vy = -1, 0
                elif current_v.direction == Direction.SOUTH: vx, vy = 0, 1
                elif current_v.direction == Direction.NORTH: vx, vy = 0, -1
                elif current_v.direction == Direction.NORTHEAST: vx, vy = 1, -1
                elif current_v.direction == Direction.SOUTHWEST: vx, vy = -1, 1
                
                # Chiếu vị trí xe kia lên vector di chuyển của mình (Dot product)
                dot_prod = dx * vx + dy * vy
                
                if dot_prod > 0: # Nghĩa là xe kia đang chắn ở PHÍA TRƯỚC mặt
                    if current_v.direction != other.direction:
                        # Hai xe khác hướng lỡ đâm nhau ở ngã tư -> Xe ID nhỏ hơn phải đợi
                        if id(current_v) < id(other):
                            return False 
                    else:
                        # Đi cùng hướng thì luôn phải phanh giữ khoảng cách
                        return False
        return True

    def is_lane_safe(self, current_v, target_y):
        cw, ch = current_v.get_body_width(), current_v.get_body_height()
        blind_spot = pygame.Rect(current_v.x - 100, target_y, cw + 200, ch)
        for other in self.vehicles:
            if other == current_v: continue
            other_rect = pygame.Rect(other.x, other.y, other.get_body_width(), other.get_body_height())
            if blind_spot.colliderect(other_rect): return False
        return True

    def is_intersection_clear(self, current_v, inter):
        if current_v.direction in [Direction.SOUTH, Direction.NORTH, Direction.NORTHEAST, Direction.SOUTHWEST]: return True
        for other in self.vehicles:
            if other == current_v or current_v.direction != other.direction: continue
            if abs(current_v.y - other.y) > 20: continue 
            if current_v.direction == Direction.EAST:
                if current_v.x < inter.x and other.x > current_v.x:
                    if other.x < inter.x + self.ROAD_WIDTH + 15: return False 
            elif current_v.direction == Direction.WEST:
                if current_v.x > inter.x + self.ROAD_WIDTH and other.x < current_v.x:
                    ow = other.get_body_width()
                    if other.x + ow > inter.x - 15: return False
        return True

    def try_overtake(self, current_v):
        if not self.can_change_lane(current_v) or current_v.direction in [Direction.SOUTH, Direction.NORTH, Direction.NORTHEAST, Direction.SOUTHWEST]: return
        target_y = None
        is_emergency = current_v.name in ["Ambu", "Fire"]
        
        if current_v.direction == Direction.EAST:
            if current_v.y == self.EAST_LANE_SLOW:
                if self.is_lane_safe(current_v, self.EAST_LANE_FAST): target_y = self.EAST_LANE_FAST
                elif is_emergency and self.is_lane_safe(current_v, self.EAST_LANE_EMG): target_y = self.EAST_LANE_EMG
            elif current_v.y == self.EAST_LANE_FAST and is_emergency:
                if self.is_lane_safe(current_v, self.EAST_LANE_EMG): target_y = self.EAST_LANE_EMG
        elif current_v.direction == Direction.WEST:
            if current_v.y == self.WEST_LANE_SLOW:
                if self.is_lane_safe(current_v, self.WEST_LANE_FAST): target_y = self.WEST_LANE_FAST
                elif is_emergency and self.is_lane_safe(current_v, self.WEST_LANE_EMG): target_y = self.WEST_LANE_EMG
            elif current_v.y == self.WEST_LANE_FAST and is_emergency:
                if self.is_lane_safe(current_v, self.WEST_LANE_EMG): target_y = self.WEST_LANE_EMG

        if target_y:
            current_v.y = target_y
            self.lane_change_cooldown[id(current_v)] = self.ticks

    def return_to_slow_lane(self, current_v):
        if not self.can_change_lane(current_v): return
        if current_v.name in ["Ambu", "Fire"] or current_v.direction in [Direction.SOUTH, Direction.NORTH, Direction.NORTHEAST, Direction.SOUTHWEST]: return
        
        target_y = None
        if current_v.direction == Direction.EAST:
            if current_v.y == self.EAST_LANE_EMG: target_y = self.EAST_LANE_FAST
            elif current_v.y == self.EAST_LANE_FAST: target_y = self.EAST_LANE_SLOW
        elif current_v.direction == Direction.WEST:
            if current_v.y == self.WEST_LANE_EMG: target_y = self.WEST_LANE_FAST
            elif current_v.y == self.WEST_LANE_FAST: target_y = self.WEST_LANE_SLOW
            
        if target_y and self.is_lane_safe(current_v, target_y):
            old_y = current_v.y
            current_v.y = target_y
            if not self.check_safe_distance(current_v, 35):
                current_v.y = old_y
            else:
                self.lane_change_cooldown[id(current_v)] = self.ticks

    def get_approaching_intersection(self, v):
        if v.direction in [Direction.SOUTH, Direction.NORTH, Direction.NORTHEAST, Direction.SOUTHWEST]: return None 
        for inter in self.intersections:
            if v.direction == Direction.EAST and inter.x - 70 <= v.x < inter.x: return inter
            if v.direction == Direction.WEST and inter.x + self.ROAD_WIDTH < v.x <= inter.x + self.ROAD_WIDTH + 70: return inter
        return None

    def can_vehicle_go(self, v):
        approaching = self.get_approaching_intersection(v)
        if not approaching: return True
        if v.name in ["Ambu", "Fire"]: return True 
        
        is_green = approaching.light.can_go(v.direction)
        if not is_green: return False
        return self.is_intersection_clear(v, approaching)

    def update_all(self):
        self.ticks += 1
        for v in self.vehicles:
            self.execute_turn(v)
            light_allows = self.can_vehicle_go(v)
            is_clear_ahead_far = self.check_safe_distance(v, threshold=250)
            
            if not is_clear_ahead_far and light_allows: self.try_overtake(v)
            elif is_clear_ahead_far: self.return_to_slow_lane(v)
                
            is_safe = self.check_safe_distance(v, threshold=35)
            if is_safe: v.move(light_allows, self.vehicles)

        self.vehicles[:] = [v for v in self.vehicles if -300 < v.x < self.WIDTH + 300 and -300 < v.y < self.HEIGHT + 300]