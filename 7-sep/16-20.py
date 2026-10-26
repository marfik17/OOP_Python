# ==
# Задание 16 (Классы Line, Rect, Ellipse)
# ==

import random


class Line:
    def __init__(self, a, b, c, d):
        self.sp = (a, b)
        self.ep = (c, d)


class Rect:
    def __init__(self, a, b, c, d):
        self.sp = (a, b)
        self.ep = (c, d)


class Ellipse:
    def __init__(self, a, b, c, d):
        self.sp = (a, b)
        self.ep = (c, d)


elements = []

for i in range(217):
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    c = random.randint(1, 100)
    d = random.randint(1, 100)

    cls = random.choice([Line, Rect, Ellipse])
    obj = cls(a, b, c, d)

    elements.append(obj)


# Обнуляем координаты только у объектов класса Line
for obj in elements:
    if type(obj) == Line:
        obj.sp = (0, 0)
        obj.ep = (0, 0)


# ==
# Задание 17 (Класс TriangleChecker)
# ==

class TriangleChecker:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def is_triangle(self):
        if not isinstance(self.a, (int, float)):
            return 1

        if not isinstance(self.b, (int, float)):
            return 1

        if not isinstance(self.c, (int, float)):
            return 1

        if self.a <= 0 or self.b <= 0 or self.c <= 0:
            return 1

        if self.a + self.b <= self.c:
            return 2

        if self.a + self.c <= self.b:
            return 2

        if self.b + self.c <= self.a:
            return 2

        return 3


# Считываем три числа
a, b, c = map(int, input().split())

tr = TriangleChecker(a, b, c)

print(tr.is_triangle())


# ==
# Задание 18 (Класс Graph)
# ==

class Graph:
    def __init__(self, data):
        self.data = data.copy()
        self.is_show = True

    def set_data(self, data):
        self.data = data.copy()

    def show_table(self):
        if self.is_show:
            print(*self.data)
        else:
            print('Отображение данных закрыто')

    def show_graph(self):
        if self.is_show:
            print('Графическое отображение данных:', *self.data)
        else:
            print('Отображение данных закрыто')

    def show_bar(self):
        if self.is_show:
            print('Столбчатая диаграмма:', *self.data)
        else:
            print('Отображение данных закрыто')

    def set_show(self, fl_show):
        self.is_show = fl_show


# Считывание списка из входного потока
data_graph = list(map(int, input().split()))

gr = Graph(data_graph)

gr.show_bar()

gr.set_show(False)

gr.show_table()


# ==
# Задание 19 (Классы CPU, Memory, MotherBoard)
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
    def __init__(self, name, cpu, *memories):
        self.name = name
        self.cpu = cpu
        self.total_mem_slots = 4
        self.mem_slots = list(memories[:4])

    def get_config(self):
        memory = '; '.join(
            f'{mem.name} - {mem.volume}'
            for mem in self.mem_slots
        )

        return [
            f'Материнская плата: {self.name}',
            f'Центральный процессор: {self.cpu.name}, {self.cpu.fr}',
            f'Слотов памяти: {self.total_mem_slots}',
            f'Память: {memory}'
        ]


cpu = CPU('Intel Core i5', 3200)

mem1 = Memory('Kingston', 8192)
mem2 = Memory('Samsung', 16384)

mb = MotherBoard(
    'ASUS Prime',
    cpu,
    mem1,
    mem2
)


# ==
# Задание 20 (Класс Cart и классы товаров)
# ==

class Cart:
    def __init__(self):
        self.goods = []

    def add(self, gd):
        self.goods.append(gd)

    def remove(self, indx):
        del self.goods[indx]

    def get_list(self):
        return [
            f'{gd.name}: {gd.price}'
            for gd in self.goods
        ]


class Table:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class TV:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Notebook:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Cup:
    def __init__(self, name, price):
        self.name = name
        self.price = price


cart = Cart()

tv1 = TV('Samsung TV', 50000)
tv2 = TV('LG TV', 45000)

table1 = Table('Компьютерный стол', 15000)

notebook1 = Notebook('Lenovo IdeaPad', 60000)
notebook2 = Notebook('ASUS VivoBook', 70000)

cup1 = Cup('Кружка белая', 500)


cart.add(tv1)
cart.add(tv2)
cart.add(table1)
cart.add(notebook1)
cart.add(notebook2)
cart.add(cup1)
