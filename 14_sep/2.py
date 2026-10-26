from string import ascii_lowercase, digits


class TextInput:
    CHARS = "абвгдеёжзийклмнопрстуфхцчшщьыъэюя " + ascii_lowercase
    CHARS_CORRECT = CHARS + CHARS.upper() + digits

    def __init__(self, name, size=10):
        self.check_name(name)
        self.name = name
        self.size = size

    @classmethod
    def check_name(cls, name):
        if not (3 <= len(name) <= 50):
            raise ValueError("некорректное поле name")
        for ch in name:
            if ch not in cls.CHARS_CORRECT:
                raise ValueError("некорректное поле name")

    def get_html(self):
        return f"<p class='login'>{self.name}: <input type='text' size={self.size} />"


class PasswordInput:
    CHARS = "абвгдеёжзийклмнопрстуфхцчшщьыъэюя " + ascii_lowercase
    CHARS_CORRECT = CHARS + CHARS.upper() + digits

    def __init__(self, name, size=10):
        self.check_name(name)
        self.name = name
        self.size = size

    @classmethod
    def check_name(cls, name):
        if not (3 <= len(name) <= 50):
            raise ValueError("некорректное поле name")
        for ch in name:
            if ch not in cls.CHARS_CORRECT:
                raise ValueError("некорректное поле name")

    def get_html(self):
        return f"<p class='password'>{self.name}: <input type='text' size={self.size} />"