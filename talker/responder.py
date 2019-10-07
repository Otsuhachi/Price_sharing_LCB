from talker.dictionary import Dictionary
import re


class Responder:
    def __init__(self):
        self.__dictionary = Dictionary()
        self.__action_mode = None
        self.__action_value = None
        self.__confirm_phase = False

    def set_mode(self, text):
        for action in self.__dictionary.actions:
            matcher = re.search(action['pattern'], text)
            if matcher:
                self.mode = action['mode']
                return
        self.mode = None

    def response(self, text):
        if self.__confirm_phase:
            return self.confirm(text)
        if self.mode is None:
            self.set_mode(text)
        if 'add' in self.mode:
            return self.add_response(text)

    def add_response(self, text):
        responses = {
            'add1': '商品名',
            'add2': '分量(数値)',
            'add3': '価格(数値)',
            'add4': '店',
            'add5': '支店名'
        }
        prompt = "を入力してください。> "
        if not text:
            pass
        elif self.mode == 'add':
            self.__action_value = ['add']
            self.mode = 'add1'
        elif '1' in self.mode:
            self.__action_value.append(text)
            self.mode = 'add2'
        elif '2' in self.mode:
            if Responder.is_value(text):
                value = Responder.int_or_float(text)
                self.__action_value.append(value)
                self.mode = 'add3'
        elif '3' in self.mode:
            if Responder.is_int(text):
                value = int(text)
                self.__action_value.append(value)
                self.mode = 'add4'
        elif '4' in self.mode:
            self.__action_value.append(text)
            self.mode = 'add5'
        elif '5' in self.mode:
            if text[-1] == '店':
                text = text[:-1]
            self.__action_value.append(text)
            res = '商品: {}\n分量: {}\n価格: {}円\n店: {} {}店\n登録してよろしいですか？'.format(
                *self.__action_value[1:])
            self.__confirm_phase = True
            return res

        return f'{responses[self.mode]}{prompt}'

    def confirm(self, text):
        if not text or text.lower() not in ('はい', 'いいえ', 'yes', 'no'):
            return '[はい, いいえ, yes, no]のいずれかでお答えください。'
        else:
            self.__confirm_phase = False
            if text.lower() in ('はい', 'yes'):
                self.add()
                self.__action_value = None
                return '登録しました。'
            self.mode = None
            return '登録しませんでした。'

    def add(self):
        # DatabaseとModeに合わせた処理を行う。
        pass

    @property
    def mode(self):
        return self.__action_mode

    @mode.setter
    def mode(self, value):
        self.__action_mode = value

    @staticmethod
    def is_value(text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_int(text):
        try:
            int(text)
            return True
        except ValueError:
            return False

    @staticmethod
    def int_or_float(value):
        value = float(value)
        if value != int(value):
            return value
        return int(value)
