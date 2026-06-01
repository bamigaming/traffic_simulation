import pygame
import math
from core.constants import Direction

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ROAD_WIDTH = 240
        self.ROAD_START_Y = 220
        
        # BẢNG MÀU FLAT DESIGN TỐI GIẢN
        self.bg_color = (163, 206, 113)    
        self.road_color = (109, 125, 139)  
        self.curb_color = (255, 255, 255)  
        self.line_color = (255, 255, 255)  

    def draw_fillet(self, surface, cx, cy, quadrant):
        """Khóa vùng vẽ, cắt góc vỉa hè mượt mà, không tràn viền"""
        R = 35 
        C = 6  
        original_clip = surface.get_clip()
        
        if quadrant == 1:
            rect = pygame.Rect(cx, cy - R, R, R)
            surface.set_clip(rect)
            pygame.draw.rect(surface, self.road_color, rect)
            pygame.draw.circle(surface, self.curb_color, (cx + R, cy - R), R)
            pygame.draw.circle(surface, self.bg_color, (cx + R, cy - R), R - C)
        elif quadrant == 2:
            rect = pygame.Rect(cx - R, cy - R, R, R)
            surface.set_clip(rect)
            pygame.draw.rect(surface, self.road_color, rect)
            pygame.draw.circle(surface, self.curb_color, (cx - R, cy - R), R)
            pygame.draw.circle(surface, self.bg_color, (cx - R, cy - R), R - C)
        elif quadrant == 3:
            rect = pygame.Rect(cx - R, cy, R, R)
            surface.set_clip(rect)
            pygame.draw.rect(surface, self.road_color, rect)
            pygame.draw.circle(surface, self.curb_color, (cx - R, cy + R), R)
            pygame.draw.circle(surface, self.bg_color, (cx - R, cy + R), R - C)
        elif quadrant == 4:
            rect = pygame.Rect(cx, cy, R, R)
            surface.set_clip(rect)
            pygame.draw.rect(surface, self.road_color, rect)
            pygame.draw.circle(surface, self.curb_color, (cx + R, cy + R), R)
            pygame.draw.circle(surface, self.bg_color, (cx + R, cy + R), R - C)

        surface.set_clip(original_clip)

    def draw_background_and_roads(self, surface, intersections):
        surface.fill(self.bg_color)
        curb = 6 
        lane_mid_y = self.ROAD_START_Y + 120
        
        inter5 = next((i for i in intersections if i.type == "5way"), None)
        cx5, cy5 = 0, 0
        if inter5:
            cx5 = inter5.x + self.ROAD_WIDTH // 2
            cy5 = self.ROAD_START_Y + self.ROAD_WIDTH // 2

        # ==================================================
        # TẦNG 1: VẼ NỀN VỈA HÈ TRẮNG 
        # ==================================================
        # Đường thẳng (Vẽ trước)
        pygame.draw.rect(surface, self.curb_color, (0, self.ROAD_START_Y - curb, self.width, self.ROAD_WIDTH + curb*2))
        for inter in intersections:
            if inter.type == "3way": 
                pygame.draw.rect(surface, self.curb_color, (inter.x - curb, self.ROAD_START_Y, self.ROAD_WIDTH + curb*2, self.height - self.ROAD_START_Y))
            elif inter.type in ["4way", "5way"]: 
                pygame.draw.rect(surface, self.curb_color, (inter.x - curb, 0, self.ROAD_WIDTH + curb*2, self.height))
        
        # Đường chéo (Vẽ sau để đè lên góc nhọn)
        if inter5:
            length = 1000
            end_x, end_y = cx5 + length, cy5 - length
            curb_hw = (self.ROAD_WIDTH // 2) + curb
            dx_c, dy_c = curb_hw * 0.707, curb_hw * 0.707
            pygame.draw.polygon(surface, self.curb_color, [
                (cx5 - dx_c, cy5 - dy_c), (cx5 + dx_c, cy5 + dy_c),
                (end_x + dx_c, end_y + dy_c), (end_x - dx_c, end_y - dy_c)
            ])

        # ==================================================
        # TẦNG 2: VẼ MẶT ĐƯỜNG NHỰA XÁM
        # ==================================================
        # Đường thẳng (Vẽ trước)
        pygame.draw.rect(surface, self.road_color, (0, self.ROAD_START_Y, self.width, self.ROAD_WIDTH))
        for inter in intersections:
            if inter.type == "3way": 
                pygame.draw.rect(surface, self.road_color, (inter.x, self.ROAD_START_Y, self.ROAD_WIDTH, self.height - self.ROAD_START_Y))
            elif inter.type in ["4way", "5way"]: 
                pygame.draw.rect(surface, self.road_color, (inter.x, 0, self.ROAD_WIDTH, self.height))

        # Đường chéo (Vẽ đè lên TẤT CẢ để dọn sạch góc)
        if inter5:
            road_hw = self.ROAD_WIDTH // 2
            dx_r, dy_r = road_hw * 0.707, road_hw * 0.707
            pygame.draw.polygon(surface, self.road_color, [
                (cx5 - dx_r, cy5 - dy_r), (cx5 + dx_r, cy5 + dy_r),
                (end_x + dx_r, end_y + dy_r), (end_x - dx_r, end_y - dy_r)
            ])

        # ==================================================
        # TẦNG 3: BO GÓC GIAO LỘ (FIX LỖI CẮN ĐƯỜNG CHÉO)
        # ==================================================
        for inter in intersections:
            self.draw_fillet(surface, inter.x, self.ROAD_START_Y + self.ROAD_WIDTH, 3)
            self.draw_fillet(surface, inter.x + self.ROAD_WIDTH, self.ROAD_START_Y + self.ROAD_WIDTH, 4)
            
            if inter.type == "4way":
                self.draw_fillet(surface, inter.x, self.ROAD_START_Y, 2)
                self.draw_fillet(surface, inter.x + self.ROAD_WIDTH, self.ROAD_START_Y, 1)
            elif inter.type == "5way":
                self.draw_fillet(surface, inter.x, self.ROAD_START_Y, 2)
                # QUAN TRỌNG: KHÔNG bo góc 1 (Trên-Phải) của ngã 5 để bảo toàn đường chéo!

        # ==================================================
        # TẦNG 4: VẠCH KẺ GIỮA ĐƯỜNG (CHÍNH XÁC, KHÔNG DÍNH ZEBRA)
        # ==================================================
        # Trục Đông - Tây
        seg_start_x = 0
        for inter in intersections:
            seg_end_x = inter.x - 45 
            if seg_end_x > seg_start_x:
                for x in range(seg_start_x, seg_end_x, 40):
                    if x + 20 <= seg_end_x: 
                        pygame.draw.rect(surface, self.line_color, (x, lane_mid_y - 2, 20, 4))
            seg_start_x = inter.x + self.ROAD_WIDTH + 45 
            
        if seg_start_x < self.width:
            for x in range(seg_start_x, self.width, 40):
                pygame.draw.rect(surface, self.line_color, (x, lane_mid_y - 2, 20, 4))

        # Trục Bắc - Nam
        for inter in intersections:
            lane_mid_x = inter.x + self.ROAD_WIDTH // 2
            
            start_y = self.ROAD_START_Y + self.ROAD_WIDTH + 45
            for y in range(start_y, self.height, 40):
                if y + 20 <= self.height: 
                    pygame.draw.rect(surface, self.line_color, (lane_mid_x - 2, y, 4, 20))
                    
            if inter.type in ["4way", "5way"]:
                end_y = self.ROAD_START_Y - 45
                for y in range(0, end_y, 40):
                    if y + 20 <= end_y: 
                        pygame.draw.rect(surface, self.line_color, (lane_mid_x - 2, y, 4, 20))

        # Đường chéo ngã 5 (Thêm nét đứt cho đường chéo)
        if inter5:
            current_dist = (self.ROAD_WIDTH // 2) + 45 # Lùi cách xa ngã tư 45px
            max_dist = 1000
            while current_dist < max_dist:
                dash_start_x = cx5 + current_dist * 0.707
                dash_start_y = cy5 - current_dist * 0.707
                dash_end_x = cx5 + (current_dist + 20) * 0.707
                dash_end_y = cy5 - (current_dist + 20) * 0.707
                pygame.draw.line(surface, self.line_color, (dash_start_x, dash_start_y), (dash_end_x, dash_end_y), 4)
                current_dist += 40

        # ==================================================
        # TẦNG 5: VẠCH SANG ĐƯỜNG ZEBRA 
        # ==================================================
        for inter in intersections:
            for offset in range(10, self.ROAD_WIDTH - 10, 25): 
                pygame.draw.rect(surface, self.line_color, (inter.x + offset, self.ROAD_START_Y + self.ROAD_WIDTH + 10, 14, 30))
            if inter.type in ["4way", "5way"]:
                for offset in range(10, self.ROAD_WIDTH - 10, 25): 
                    pygame.draw.rect(surface, self.line_color, (inter.x + offset, self.ROAD_START_Y - 40, 14, 30))
            for offset in range(10, self.ROAD_WIDTH - 10, 25):
                pygame.draw.rect(surface, self.line_color, (inter.x - 40, self.ROAD_START_Y + offset, 30, 14))
                pygame.draw.rect(surface, self.line_color, (inter.x + self.ROAD_WIDTH + 10, self.ROAD_START_Y + offset, 30, 14))

    def draw_traffic_lights(self, surface, intersections):
        for inter in intersections:
            dirs = [Direction.EAST, Direction.WEST]
            if inter.type in ["3way", "4way", "5way"]: dirs.append(Direction.SOUTH)
            if inter.type in ["4way", "5way"]: dirs.append(Direction.NORTH)
            
            for dir_enum in dirs:
                pole_x, pole_y = 0, 0
                if dir_enum == Direction.EAST: 
                    pole_x, pole_y = inter.x - 50, self.ROAD_START_Y + self.ROAD_WIDTH + 25
                elif dir_enum == Direction.WEST:
                    if inter.type == "5way":
                        # FIX LỖI: Dời cột đèn nhường chỗ cho đường chéo
                        pole_x, pole_y = inter.x + self.ROAD_WIDTH + 90, self.ROAD_START_Y - 140
                    else:
                        pole_x, pole_y = inter.x + self.ROAD_WIDTH + 20, self.ROAD_START_Y - 110
                elif dir_enum == Direction.SOUTH: 
                    pole_x, pole_y = inter.x - 50, self.ROAD_START_Y - 110
                elif dir_enum == Direction.NORTH: 
                    pole_x, pole_y = inter.x + self.ROAD_WIDTH + 20, self.ROAD_START_Y + self.ROAD_WIDTH + 25
                inter.light.draw_pole(surface, pole_x, pole_y, dir_enum)