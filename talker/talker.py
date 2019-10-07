from talker.responder import Responder


class Talker:
    def __init__(self):
        self.__responder = Responder()

    def dialogue(self, text):
        res = self.__responder.response(text)
        # return f'mode: {self.__responder.mode}\n{res}'
        return f'{res}'
