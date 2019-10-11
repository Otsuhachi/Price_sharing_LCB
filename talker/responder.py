from talker.dictionary import Dictionary
import psycopg2


class Responder:
    """AIの応答を制御する思考エンジンの基底クラスです。

    Attributes:
        state (int or str): 実行状態を表します。
            0が初期化直後で、処理を完了し不要になった状態を"end"としてください。
    """
    def __init__(self):
        """初期化します。
        """
        self.__state = 0
        self.__create_cursor()

    def __create_cursor(self):
        self.__connection = psycopg2.connect(Dictionary().uri)
        self.__connection.autocommit = True
        self.__cursor = self.__connection.cursor()

    def response(self, text):
        """AIの応答を生成し、返します。
        子クラスにて独自定義してください。

        Args:
            text (str): ユーザーからの入力。
        """
        raise NotImplementedError

    @property
    def state(self):
        """現在の実行状態です。
        0, 'end' 以外の状態は独自に設定可能です。

        Returns:
            int or str: 現在の実行状態。
        """
        return self.__state

    def exit(self):
        """現在の実行状態を'end'に設定します。
        """
        self.__state = 'end'
        self.cursor.close()
        self.__connection.close()

    @state.setter
    def state(self, value):
        """現在の実行状態を設定します。
        0, 'end'を指定することはできません。

        Args:
            value (int or str): 現在の実行状態。
        """
        if value in (0, 'end'):
            raise ValueError
        self.__state = value

    @staticmethod
    def text2value(text, mode='both'):
        """文字列を数値変換し、返します。

        modeで変換結果が変わります。
        modeに指定できる引数は[float, int, 'both']のいずれかで、それ以外を与えた場合は'both'になります。

        Examples:
            Case1:
                >>> from talker.responder import Responder as R
                >>> a='2'
                >>> R.text2value(a)
                2
                >>> R.text2value(a, int)
                2
                >>> R.text2value(a, float)
                2.0
                >>> str(R.text2value('a'))
                'None'

            Case2:
                >>> from talker.responder import Responder as R
                >>> a='2.3'
                >>> R.text2value(a)
                2.3
                >>> R.text2value(a, int)
                2
                >>> R.text2value(a, float)
                2.3

        Args:
            text (str): 数値に変換したい文字列。
            mode (str or int or float, optional): 変換モード。詳しくはExamplesを参照してください。

        Returns:
            int or float or None: 数値型。変換できなければNoneが返ります。
        """
        if mode not in (int, float, 'both'):
            mode = 'both'
        try:
            f = float(text)
            if mode == float:
                return f
        except ValueError:
            return None
        try:
            i = int(f)
        except ValueError:
            if mode == 'both':
                return f
            return None
        if mode == 'both':
            if f == i:
                return i
            return f
        elif mode == int:
            return i

    @property
    def cursor(self):
        return self.__cursor


class AddResponder(Responder):
    """商品情報を追加するためのAIの思考エンジンクラスです。

    Attributes:
        keys (tuple[str]): stateに設定するキー群です。 これを使って商品登録の進捗を制御します。
        infomation: 商品情報です。
    """
    def __init__(self, **kwargs):
        """商品情報を追加します。
        """
        super().__init__()
        self.__load()
        self.__infomation = {x: False for x in self.keys}
        for key in kwargs:
            if key in self.keys:
                self.__infomation[key] = kwargs[key]

    def __load(self):
        dics = Dictionary().add_responses
        self.__keys = []
        self.__responses = {}
        for dic in dics:
            for key in dic:
                self.__keys.append(key)
                self.__responses[key] = dic[key]

    def response(self, text):
        """AIの応答を生成し、返します。
        受け取った文字列に応じて、商品情報登録の進捗制御、返信メッセージの作成を行います。

        Args:
            text (str): ユーザーからの入力。

        Returns:
            str: AIからの応答。
        """
        res = self.add_infomation(text)
        return res

    def add_infomation(self, text):
        previous = self.state
        self.set_state()
        if previous == 0:
            return self.responses[self.state]
        self.set_infomation_value(text)
        if self.info['confirm'] in ('ok', 'no'):
            if self.info['confirm'] == 'ok':
                self.push_database()
                res = "登録しました。"
            else:
                res = "登録を取り消しました。"
            self.exit()
            return res
        if self.state == 'confirm':
            return self.responses[self.state].format(*self.values)
        return self.responses[self.state]

    def set_infomation_value(self, text):
        state = self.state
        if state == 'name':
            if text:
                self.info['name'] = text
        elif state == 'amount':
            value = self.text2value(text)
            if value is not None:
                self.info['amount'] = value
        elif state == 'price':
            value = self.text2value(text, int)
            if value is not None:
                self.info['price'] = value
        elif state == 'shop':
            if text:
                self.info['shop'] = text
        elif state == 'shop_branch':
            if text:
                if text[-1] != '店':
                    text += '店'
                self.info['shop_branch'] = text
        elif state == 'confirm':
            ok_word = ('yes', 'y', 'はい')
            no_word = ('no', 'n', 'いいえ')
            if text:
                text = text.lower()
                if text in ok_word:
                    self.info['confirm'] = 'ok'
                elif text in no_word:
                    self.info['confirm'] = 'no'
        self.set_state()

    def push_database(self):
        del_data = (self.info['name'], self.info['amount'], self.info['shop'],
                    self.info['shop_branch'])
        data = tuple(self.info[key] for key in self.keys if key != 'confirm')

        sqls = [
            "delete from products where name='{}' and amount={} and shop='{}' and shop_branch='{}'"
            .format(*del_data), f"insert into products values {data}"
        ]
        for sql in sqls:
            self.cursor.execute(sql)

    def set_state(self):
        if self.state == 0:
            self.state = 'name'
            return
        for key in self.keys:
            data = self.info[key]
            if not data and data is not None:
                self.state = key
                return

    def show(self):
        """現在の商品情報を表示します。
        """
        print("商品情報")
        for key in self.info:
            print(f"{key}: {self.info[key]}")

    @property
    def values(self):
        i = self.info
        return (i['name'], i['amount'], i['price'], i['shop'],
                i['shop_branch'])

    @property
    def keys(self):
        return self.__keys

    @property
    def info(self):
        return self.__infomation

    @property
    def responses(self):
        return self.__responses


class ProductsResponder(Responder):
    def __init__(self):
        super().__init__()
        self.__adder = None

    def response(self, text):
        if self.adder is not None:
            res = self.adder.response(text)
            if self.adder.state == 'end':
                self.adder = None
                self.exit()
            return res
        else:
            res = self.check_database(text)
            self.exit()
            return res

    def check_database(self, text):
        sql = f"select * from products where name='{text}' order by price/amount limit 3"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return "\n".join(self.format_products(row) for row in rows)

    @staticmethod
    def format_products(row):
        name, amount, price, shop, shop_branch = row
        if int(amount) == amount:
            amount = int(amount)
        return f"{name}({amount}): {price}円 | {shop} {shop_branch}"

    @property
    def adder(self):
        return self.__adder
