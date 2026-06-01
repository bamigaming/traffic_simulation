import pygame
import sys
from core.environment import TrafficLight, Intersection
from core.renderer import Renderer
from core.controller import TrafficController

pygame.init()
WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart City Traffic - Clean Architecture MVC")
clock = pygame.time.Clock()

# 1. Khởi tạo Dữ liệu (Model)
light_common = TrafficLight(is_five_way=False)
light5 = TrafficLight(is_five_way=True)
intersections = [
    Intersection(250, 220, "3way", light_common),
    Intersection(750, 220, "4way", light_common),
    Intersection(1250, 220, "5way", light5)
]
vehicles = []

# 2. Khởi tạo Đồ họa (View) và Não bộ (Controller)
renderer = Renderer(WIDTH, HEIGHT)
controller = TrafficController(intersections, vehicles)

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 900)

# 3. Vòng lặp Game (Game Loop)
running = True
while running:
    # A. Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_EVENT:
            controller.spawn_vehicle()
            
    # B. Cập nhật Model & Logic
    light_common.update()
    light5.update()
    controller.update_all()

    # C. Cập nhật View
    renderer.draw_background_and_roads(screen, intersections)
    renderer.draw_traffic_lights(screen, intersections)
    
    for v in vehicles:
        v.draw_basic(screen)

    pygame.display.flip()
    clock.tick(40)

pygame.quit()
sys.exit()