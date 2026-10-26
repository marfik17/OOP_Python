# ==
# Задача 1. Класс Goods и функции setattr()
# ==
class Goods:
    title = "Мороженое"
    weight = 150
    tp = "Еда"
    price = 100


# Изменение существующего атрибута и добавление нового с помощью setattr()
setattr(Goods, "price", 2048)
setattr(Goods, "inflation", 100)

print("--- Задача 1 ---")
print(f"Price: {Goods.price}, Inflation: {Goods.inflation}\n")


# ==
# Задача 2. Класс TravelBlog и счетчик блогов
# ==
class TravelBlog:
    total_blogs = 0


# Создание первого экземпляра
tb1 = TravelBlog()
tb1.name = "Франция"
tb1.days = 6
TravelBlog.total_blogs += 1

# Создание второго экземпляра
tb2 = TravelBlog()
tb2.name = "Италия"
tb2.days = 5
TravelBlog.total_blogs += 1

print("--- Задача 2 ---")
print(f"Итоговое значение total_blogs: {TravelBlog.total_blogs}\n")


# ==
# Задача 3. Класс MediaPlayer
# ==
class MediaPlayer:

    def open(self, file):
        self.filename = file

    def play(self):
        print(f"Воспроизведение {self.filename}")


print("--- Задача 3 ---")
media1 = MediaPlayer()
media2 = MediaPlayer()

media1.open("song.mp3")
media2.open("movie.mp4")

media1.play()
media2.play()
print()


# ==
# Задача 4. Класс Money с инициализатором
# ==
class Money:

    def __init__(self, money):
        self.money = money


print("--- Задача 4 ---")
my_money = Money(100)
print(f"Объект my_money содержит: {my_money.money}\n")


# ==
# Задача 5. Класс Point с необязательным аргументом
# ==
class Point:

    def __init__(self, x, y, color="black"):
        self.x = x
        self.y = y
        self.color = color


print("--- Задача 5 ---")
# Список из 3 точек (одна без цвета, две с цветом)
points = [Point(10, 20), Point(12, 5, "red"), Point(0, 0, "blue")]

for i, p in enumerate(points, 1):
    print(f"Точка {i}: x={p.x}, y={p.y}, color='{p.color}'")
print()


# ==
# Задача 6. Класс DataBase и методы парсинга
# ==
class DataBase:
    lst_data = []
    FIELDS = ("id", "name", "old", "salary")

    def insert(self, data):
        for line in data:
            # Разбиваем строку по пробелам и создаем словарь по ключам из FIELDS
            values = line.split()
            row_dict = dict(zip(self.FIELDS, values))
            self.lst_data.append(row_dict)

    def select(self, a, b):
        # Возвращаем копию среза списка в диапазоне индексов [a; b] (включая b)
        return self.lst_data[a : b + 1]


print("--- Задача 6 ---")
db = DataBase()
db.insert(["1 Сергей 35 120000", "2 Анна 28 90000", "3 Иван 42 150000"])
# Выберем элементы с индексами от 0 до 1
selected_data = db.select(0, 1)
print(f"Выбранные данные: {selected_data}\n")


# ==
# Задача 7. Класс Graph и управление флагом отображения
# ==
class Graph:

    def __init__(self, data):
        self.data = list(data)
        self.is_show = True

    def show_table(self):
        if not self.is_show:
            print("Отображение данных закрыто")
        else:
            print(" ".join(map(str, self.data)))

    def set_show(self, fl_show):
        self.is_show = fl_show


print("--- Задача 7 ---")
graph = Graph([1, 2, 3, 4, 5])
graph.show_table()  # Выведет данные
graph.set_show(False)
graph.show_table()  # Выведет сообщение о закрытии
print()


# ==
# Задача 8. Классы комплектующих ПК
# ==
class CPU:

    def __init__(self, name, fr):
        self.name = name
        self.fr = fr


class Memory:

    def __init__(self, name, volume):
        self.name = name
        self.volume = volume


class MotherBoard:

    def __init__(self, name, cpu, *mem_slots):
        self.name = name
        self.cpu = cpu
        # Ограничиваем количество планок памяти до 4 элементов
        self.mem_slots = list(mem_slots[:4])

    def get_config(self):
        # Формируем строку со сведениями о подключенной памяти
        mem_info = ", ".join(
            [f"{m.name} ({m.volume}GB)" for m in self.mem_slots]
        )
        return [
            f"Материнская плата: {self.name}",
            f"Процессор: {self.cpu.name}, Частота: {self.cpu.fr}GHz",
            f"Всего слотов памяти: 4",
            f"Подключенная память: {mem_info if mem_info else 'Нет памяти'}",
        ]


print("--- Задача 8 ---")
cpu = CPU("Intel Core i7", 3.6)
mem1 = Memory("Kingston", 16)
mem2 = Memory("Corsair", 16)
mb = MotherBoard("ASUS Prime", cpu, mem1, mem2)

for line in mb.get_config():
    print(line)
print()


# ==
# Задача 9. Полиморфизм и наследование фигур
# ==
class Figure:

    def __init__(self, coords=None, width=1, color="black"):
        self.coords = coords if coords else []
        self.width = width
        self.color = color

    def draw(self):
        print("Рисуется фигура")


class Line(Figure):

    def draw(self):
        print("Рисуется линия")


class Rect(Figure):

    def draw(self):
        print("Рисуется прямоугольник")


class Ellipse(Figure):

    def draw(self):
        print("Рисуется эллипс")


class Triangle(Figure):

    def draw(self):
        print("Рисуется треугольник")


print("--- Задача 9 ---")
#Общий список с объектами трех типов
figures = [Line(), Rect(), Ellipse()]

#Один цикл для обхода всех фигур
for fig in figures:
    fig.draw()

print("\nДобавляем Triangle в список:")
#Не меняя цикл, добавляем новый объект
figures.append(Triangle())

for fig in figures:
    fig.draw()

