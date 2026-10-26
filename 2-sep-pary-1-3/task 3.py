class Car:
    def __init__(self):
        
        self._engine_temperature = 20

    
    def start_engine(self):
        self._engine_temperature = 90
        print("Двигатель прогрет")

    
    def drive(self):
        if self._engine_temperature >= 90:
            print("Поехали!")
        else:
            print("Ошибка! Двигатель не прогрет, ехать нельзя.")


my_car = Car()

print("--- Попытка уехать без прогрева ---")
my_car.drive() 

print("\n--- Попытка уехать по правилам ---")
my_car.start_engine()
my_car.drive()

print("\n--- Прямое обращение извне ---")
print(f"Текущая температура внутри класса: {my_car._engine_temperature}°C")
