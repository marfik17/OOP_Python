#Базовый класс 
class Figure:
    def __init__(self, coords: tuple, width: int | float, color: str):
        self.coords = coords
        self.width = width
        self.color = color

    def draw(self):
        print("Рисуется фигура.")




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


#Задача 8: Добавление нового класса Triangle
class Triangle(Figure):
    def __init__(self, coords: tuple, width: int | float, color: str):
        # Наследуем базовые свойства без добавления уникальных числовых параметров
        super().__init__(coords, width, color)

    
    def draw(self):
        print("Рисуется треугольник...")


# Главная программа 


figures_list = [
    Line(coords=(0, 0, 10, 0), width=2, color="black", length=10.0),
    Rect(coords=(5, 5), width=1, color="red", height=20.5),
    Ellipse(coords=(10, 10), width=3, color="blue", radius=7.0),
    Triangle(coords=(0, 0, 3, 4, 6, 0), width=1, color="green")  # Новый объект
]

#не изменен ни на одну строчку!
print("--- Проверка работы полиморфизма (с треугольником) ---")
for figure in figures_list:
    figure.draw()
