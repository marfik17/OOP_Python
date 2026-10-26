class Graph:
    def __init__(self, x=0, y=0, scale=1.0):
        self._x = x
        self._y = y
        self._scale = scale

    def move(self, dx, dy):
        self._x += dx
        self._y += dy

    def change_scale(self, factor):
        self._scale *= factor

    def __str__(self):
        return f"Координаты: ({self._x}, {self._y}), Масштаб: {self._scale}"

graph1 = Graph(0, 0, 1.0)
graph2 = Graph(0, 0, 1.0)
graph3 = Graph(0, 0, 1.0)

graph1.move(5, 10)

graph2.change_scale(2.5)


print("Первый график:", graph1)
print("Второй график:", graph2)
print("Третий график:", graph3)
