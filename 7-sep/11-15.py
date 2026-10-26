# ==
# Задание 11 (Класс StreamData)
# ==
class StreamData:
    def create(self, fields, lst_values):
        if len(fields) != len(lst_values):
            return False

        for i in range(len(fields)):
            setattr(self, fields[i], lst_values[i])

        return True


import sys


class StreamReader:
    FIELDS = ('id', 'title', 'pages')

    def readlines(self):
        lst_in = list(map(str.strip, sys.stdin.readlines()))
        sd = StreamData()
        res = sd.create(self.FIELDS, lst_in)
        return sd, res


sr = StreamReader()
data, result = sr.readlines()


# ==
# Задание 12 (Класс DataBase)
# ==
class DataBase:
    lst_data = []
    FIELDS = ('id', 'name', 'old', 'salary')

    def insert(self, data):
        for line in data:
            values = line.split()
            d = dict(zip(self.FIELDS, values))
            self.lst_data.append(d)

    def select(self, a, b):
        return self.lst_data[a:b + 1]


# ==
# Задание 13 (Класс Translator)
# ==
class Translator:
    def add(self, eng, rus):
        if 'tr' not in self.__dict__:
            self.tr = {}

        self.tr.setdefault(eng, [])

        if rus not in self.tr[eng]:
            self.tr[eng].append(rus)

    def remove(self, eng):
        if eng in self.tr:
            del self.tr[eng]

    def translate(self, eng):
        if eng in self.tr:
            return self.tr[eng]

        return False


tr = Translator()

tr.add('tree', 'дерево')
tr.add('car', 'машина')
tr.add('car', 'автомобиль')
tr.add('leaf', 'лист')
tr.add('river', 'река')
tr.add('go', 'идти')
tr.add('go', 'ехать')
tr.add('go', 'ходить')
tr.add('milk', 'молоко')

tr.remove('car')

words = tr.translate('go')
print(*words)


# ==
# Задание 14 (Класс Money)
# ==
class Money:
    def __init__(self, money):
        self.money = money


my_money = Money(100)
your_money = Money(1000)


# ==
# Задание 15 (Класс Point)
# ==
class Point:
    def __init__(self, x, y, color='black'):
        self.x = x
        self.y = y
        self.color = color


points = []

for i in range(1000):
    x = 1 + i * 2
    y = 1 + i * 2

    points.append(Point(x, y))

points[1].color = 'yellow'
