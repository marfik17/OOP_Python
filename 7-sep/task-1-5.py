
# Задание 1
class DataBase:
    pk = 1
    title = "Классы и объекты"
    author = "Сергей Балакирев"
    views = 14356
    comments = 12

# Задание 2
class Goods:
    title = "Мороженое"
    weight = 154
    tp = "Еда"
    price = 1024

# Изменяем цену и добавляем инфляцию
Goods.price = 2048
Goods.inflation = 100

# Задание 3
class Car:
    pass

# Добавляем атрибуты динамически
setattr(Car, 'model', "Тойота")
setattr(Car, 'color', "Розовый")
setattr(Car, 'number', "П111УУ77")

# Вывод на экран значения из __dict__
print("Задание 3 (цвет из __dict__):", Car.__dict__['color'])

# Задание 4
class Notes:
    uid = 1005435
    title = "Шутка"
    author = "И.С. Бах"
    pages = 2

# Читаем автора через getattr
print("Задание 4 (автор через getattr):", getattr(Notes, 'author'))

# Задание 5
class Dictionary:
    rus = "Питон"
    eng = "Python"

# Ищем rus_word, если нет — вернет False
print("Задание 5 (поиск rus_word):", getattr(Dictionary, 'rus_word', False))
