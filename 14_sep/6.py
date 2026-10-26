class Message:
    def __init__(self, text):
        self.text = text
        self.fl_like = False


class Viber:
    msgs = {}

    @classmethod
    def add_message(cls, msg):
        cls.msgs[id(msg)] = msg

    @classmethod
    def remove_message(cls, msg):
        cls.msgs.pop(id(msg), None)

    @classmethod
    def set_like(cls, msg):
        msg.fl_like = not msg.fl_like

    @classmethod
    def total_messages(cls):
        return len(cls.msgs)