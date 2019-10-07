import re
from random import choice

from talker.dictionary import Dictionary


class Responder:
    """AIの応答を制御する思考エンジンの基底クラスです。
    継承して使用してください。

    Methods:
        response(str): ユーザーからの入力を受け取り、思考結果を返します。

    Attributes:
        name: Responderオブジェクトの名前。
        dictionary: 応答定義api。
    """
    def __init__(self, name, dictionary):
        """文字列を受け取り、自身のnameに設定します。
        辞書を受け取り、自身のdictionaryに保持します。

        Args:
            name (str): 思考エンジンの名前。
        """
        self.__name = name
        self.__dictionary = dictionary

    def response(self, *args):
        """ユーザーからの入力を受け取り、思考結果を返します。
        """
        pass

    @property
    def name(self):
        """思考エンジンの名前です。

        Returns:
            str: 思考エンジンの名前。
        """
        return self.__name

    @property
    def dictionary(self):
        """思考エンジンの応答リストです。

        Returns:
            list[str or dict]: 思考エンジンの応答リスト。
        """
        return self.__dictionary


class WhatResponder(Responder):
    """AIの応答を制御する思考エンジンクラスです。
    入力に対して疑問形で聞き返します。
    """
    def response(self, text):
        """ユーザーからの入力を受け取り、f'{text}ってなに？'という形式で返します。

        Args:
            text (str): ユーザーからの入力。

        Returns:
            str: AIの応答。+66
        """
        return f'{text}ってなに？'


class RandomResponder(Responder):
    """AIの応答を制御する思考エンジンクラスです。
    登録された文字列からランダムなものを返します。
    """
    def response(self, _):
        """ユーザーからの入力は受け取るが、使用せずにランダムな応答を返します。

        Args:
            _ (str): ユーザーからの入力。

        Returns:
            str: AIの応答。
        """
        return choice(self.dictionary.random)


class PatternResponder(RandomResponder):
    """AIの応答を制御する思考エンジンクラスです。
    登録されたパターンに反応し、関連する応答を返します。
    """
    def response(self, text):
        for ptn in self.dictionary.pattern:
            matcher = re.search(ptn['pattern'], text)
            if matcher:
                text = choice(ptn['phrases'])
                return text.replace('%match%', matcher[0])
        return choice(self.dictionary.random)


if __name__ == '__main__':
    pres = PatternResponder('Pattern', Dictionary())
    prompt = f'{pres.name}: '
    while True:
        text = input('> ')
        if not text or text.lower() == 'exit':
            break
        print(pres.response(text))
