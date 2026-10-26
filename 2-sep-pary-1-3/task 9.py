import math

#1 Инкапсуляция: Базовый класс
class Figure:
    def __init__(self, coords: tuple):
        
        self._coords = coords  

    
    def get_coords(self):
        return self._coords

    
    def set_coords(self, new_coords: tuple):
        self._coords = new_coords

   
    def calculate_area(self):
        return 0.0


#2. Наследование и 3. Полиморфизм: Дочерние классы

#Класс Круг
class Circle(Figure):
    def __init__(self, coords: tuple, radius: float):
        super().__init__(coords)  
        self.radius = radius      

    
    def calculate_area(self):
        return math.pi * (self.radius ** 2)


# Класс Квадрат
class Square(Figure):
    def __init__(self, coords: tuple, side: float):
        super().__init__(coords)  
        self.side = side          

    
    def calculate_area(self):
        return self.side ** 2


#

#
shapes_list = [
    Circle(coords=(0, 0), radius=5.0),
    Square(coords=(2, 2), side=4.0),
    Circle(coords=(10, 10), radius=2.5),
    Square(coords=(5, -1), side=3.0),
    Circle(coords=(-3, 4), radius=1.0)
]

total_area = 0.0

print("--- Расчет площадей фигур ---")

for shape in shapes_list:
    current_area = shape.calculate_area()
    total_area += current_area
    
    print(f"Фигура в {shape.get_coords()}: площадь = {current_area:.2f}")

print("-" * 30)
print(f"Общая площадь всех фигур в списке: {total_area:.2f}")
