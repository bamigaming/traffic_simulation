from abc import ABC, abstractmethod

# Lớp trừu tượng (Interface) bắt buộc mọi cách lái xe phải có hàm move()
class DriverStrategy(ABC):
    @abstractmethod
    def move(self, vehicle, light_allows):
        pass

# Tài xế bình thường: Tuân thủ đèn giao thông, đi đúng tốc độ
class NormalDriver(DriverStrategy):
    def move(self, vehicle, light_allows):
        if not light_allows:
            vehicle.speed = 0  # Dừng lại nếu đèn đỏ/xung đột
            return
        
        vehicle.speed = vehicle.original_speed
        vehicle.update_position(vehicle.speed)

# Tài xế phóng nhanh: Tuân thủ đèn, nhưng đường thoáng là phóng (cộng thêm 4 tốc độ)
class AggressiveDriver(DriverStrategy):
    def move(self, vehicle, light_allows):
        if not light_allows:
            vehicle.speed = 0
            return
        
        vehicle.speed = vehicle.original_speed + 4
        vehicle.update_position(vehicle.speed)

# Tài xế xe ưu tiên: Vượt mọi loại đèn, phóng cực nhanh (cộng thêm 5 tốc độ)
class EmergencyDriver(DriverStrategy):
    def move(self, vehicle, light_allows):
        # Không cần kiểm tra light_allows vì xe ưu tiên được phép vượt
        vehicle.speed = vehicle.original_speed + 5
        vehicle.update_position(vehicle.speed)