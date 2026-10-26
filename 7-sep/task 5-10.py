class TravelBlog :
    total_blogs = 0
    def __init__(self, name,days):
        self.name = name
        self.days = days
        TravelBlog.total_blogs +=1
tb1 = TravelBlog('Франция',6)
tb2 = TravelBlog('Италия',5)

# ==
# Задание с экрана (TravelBlog)
# ==
class TravelBlog:
    total_blogs = 0

    def __init__(self, name, days):
        self.name = name
        self.days = days
        TravelBlog.total_blogs += 1

tb1 = TravelBlog('Франция', 6)
tb2 = TravelBlog('Италия', 5)

print(tb2.name)


# ==
# Задание 7 (Класс Figure)
# ==
class Figure:
    type_fig = 'ellipse'
    color = 'red'

fig1 = Figure()

# Добавляем локальные свойства
fig1.start_pt = (10, 5)
fig1.end_pt = (100, 20)
fig1.color = 'blue'

# Удаляем локальное свойство color
del fig1.color

# Выводим только имена локальных свойств в строку через пробел
print(*fig1.__dict__.keys())


# ==
# Задание 8 (Класс Person)
# ==
class Person:
    name = 'Сергей Балакирев'
    job = 'Программист'
    city = 'Москва'

p1 = Person()

# Проверяем наличие именно локального свойства job
print('job' in p1.__dict__)


# Задание 9 (Класс MediaPlayer)
class MediaPlayer:
    def open(self, file):
        self.filename = file

    def play(self):
        print(f"Воспроизведение {self.filename}")

media1 = MediaPlayer()
media2 = MediaPlayer()

media1.open("filemedia1")
media2.open("filemedia2")

media1.play()
media2.play()
