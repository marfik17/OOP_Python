#  Базовый класс 
class Figure:
    def __init__(self, coords: tuple, width: int | float, color: str):
        self.coords = coords
        self.width = width
        self.color = color

    
    def draw(self):
        print("Рисуется фигура.")


#  Дочерние классы с переопределением метода draw

class Line(Figure):
    def __init__(self, coords: tuple, width: int | float, color: str, length: float):
        super().__init__(coords, width, color)
        self.length = length

    
    def draw(self):
        print("Рисуется линия...")


class Rect(Figure):
    def __init__(self, coords: tuple, width: int | float, color: str, height: float):
        super().__init__(coords, width, color)
        self.height = height

    
    def draw(self):
        print("Рисуется прямоугольник...")


class Ellipse(Figure):
    def __init__(self, coords: tuple, width: int | float, color: str, radius: float):
        super().__init__(coords, width, color)
        self.radius = radius

   
    def draw(self):
        print("Рисуется эллипс...")


# === Главная программа ===

figures_list = [
    Line(coords=(0, 0, 10, 0), width=2, color="black", length=10.0),
    Rect(coords=(5, 5), width=1, color="red", height=20.5),
    Ellipse(coords=(10, 10), width=3, color="blue", radius=7.0)
]
print("--- Демонстрация полиморфизма ---")
for figure in figures_list:
    figure.draw()
