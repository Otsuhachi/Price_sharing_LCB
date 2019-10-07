from talker.dictionary import Dictionary
from talker.responder import PatternResponder, RandomResponder, WhatResponder


class Talker:
    """人工無能コアクラスです。

    Attributes:
        name (str): 人工無能の名前。
        responder_name (str): 現在の応答クラスの名前。
    """
    def __init__(self, name):
        """文字列を受けとり、コアインスタンスの名前に設定します。
        respondersを生成し、保持します。
        Dictionaryインスタンスを生成し、保持します。
        current_modeを設定し、保持します。
        current_modeに対応したResponderを生成し、保持します。

        Args:
            name (str): 人工無能の名前。
        """
        self.__name = name
        self.__dictionary = Dictionary()
        self.__responders = {
            'pattern': PatternResponder,
            'random': RandomResponder,
            'what': WhatResponder
        }
        self.__current_mode = 'pattern'
        self.change_responder()

    def change_responder(self, mode=None):
        """current_modeに対応するResponderを生成し、保持します。
        modeを指定することでResponderを指定して生成することができます。
        また、指定しなかった場合にはcurrent_modeとResponderの種類が一致するよう動作します。

        Args:
            mode (str, optional): Responderの種類。 指定しなければ保守します。
        """
        if mode is not None:
            self.__current_mode = mode.lower()
        self.__responder = self.__responders[self.__current_mode](
            self.__current_mode.capitalize(), self.__dictionary)

    def dialogue(self, text):
        """ユーザーからの入力を受け取り、Responderに処理させた結果を返します。

        Args:
            text (str): ユーザーからの入力。

        Returns:
            str: AIの応答。
        """
        response = self.__responder.response(text)
        print(f"Response: {response}")
        return response

    @property
    def name(self):
        """人工無能インスタンスの名前です。

        Returns:
            str: 人工無能インスタンスの名前。
        """
        return self.__name

    @property
    def responder_name(self):
        """保持しているResponderの名前です。

        Returns:
            str: Responderの名前。
        """
        return self.__responder.name
