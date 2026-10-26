from string import ascii_lowercase, digits


class CardCheck:
    CHARS_FOR_NAME = ascii_lowercase.upper() + digits

    @staticmethod
    def check_card_number(number):
        if not isinstance(number, str) or len(number) != 19:
            return False

        for i, ch in enumerate(number):
            if i in (4, 9, 14):
                if ch != '-':
                    return False
            else:
                if not ch.isdigit():
                    return False

        return True

    @classmethod
    def check_name(cls, name):
        if not isinstance(name, str):
            return False

        parts = name.split(' ')
        if len(parts) != 2:
            return False

        for part in parts:
            if not part:
                return False
            for ch in part:
                if ch not in cls.CHARS_FOR_NAME:
                    return False

        return True