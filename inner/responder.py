from inner.loader import Loader
import psycopg2
from inner.funcs import generate_words


class Responder:
    """AIの応答を制御する思考エンジンの基底クラスです。

    Attributes:
        state (int or str): 実行状態を表します。
            0が初期化直後で、処理を完了し不要になった状態を"end"としてください。
        connection(psycopg2.connect): データベースとの接続です。
        cursor(connect.cursor): カーソルです。
    """
    def __create_cursor(self, commit=False):
        """データベースの接続とカーソルを用意します。

        Args:
            commit (bool, optional): sqlを発行した際、データベースに結果を反映するかどうか。 標準では反映させません。
        """
        self.__connection = psycopg2.connect(Loader().uri)
        self.__connection.autocommit = commit
        self.__cursor = self.__connection.cursor()

    def __init__(self):
        """初期化します。
        """
        self.__state = 0
        self.__create_cursor(True)

    def end(self):
        """現在の実行状態を'end'に設定します。
        """
        self.__state = 'end'

    def exit(self):
        """終了処理を行います。
        """
        self.cursor.close()
        self.connection.close()

    def response(self, text):
        """AIの応答を生成し、返します。
        子クラスにて独自定義してください。

        Args:
            text (str): ユーザーからの入力。
        """
        raise NotImplementedError

    @property
    def connection(self):
        """データベースの接続です。

        Returns:
            psycopg2.connect: データベースの接続。
        """
        return self.__connection

    @property
    def cursor(self):
        """sqlの発行を行い、結果を格納します。

        Returns:
            connect.cursor: カーソル。
        """
        return self.__cursor

    @property
    def state(self):
        """現在の実行状態です。
        0, 'end' 以外の状態は独自に設定可能です。

        Returns:
            int or str: 現在の実行状態。
        """
        return self.__state

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
    def text_to_value(text, mode='both'):
        """文字列を数値変換し、返します。

        modeで変換結果が変わります。
        modeに指定できる引数は[float, int, 'both']のいずれかで、それ以外を与えた場合は'both'になります。

        Examples:
            Case1:
                >>> from talker.responder import Responder as R
                >>> a='2'
                >>> R.text_to_value(a)
                2
                >>> R.text_to_value(a, int)
                2
                >>> R.text_to_value(a, float)
                2.0
                >>> str(R.text_to_value('a'))
                'None'

            Case2:
                >>> from talker.responder import Responder as R
                >>> a='2.3'
                >>> R.text_to_value(a)
                2.3
                >>> R.text_to_value(a, int)
                2
                >>> R.text_to_value(a, float)
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


class AddResponder(Responder):
    """商品情報を追加するためのレスポンダです。

    Attributes:
        keys (tuple[str]): stateに設定するキー群です。 これを使って商品登録の進捗を制御します。
        info: 商品情報の辞書です。
        values(tuple[any]): 商品情報のタプルです。
        responses(dict): 応答パターンです。
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
        """反応する文字列パターンを読み込みます。
        また、設定に必要なキー群を読み込み設定します。
        """
        patterns = Loader().add_responses
        self.__keys = []
        self.__responses = {}
        for pattern in patterns:
            for key in pattern:
                self.__keys.append(key)
                self.__responses[key] = pattern[key]

    def add_infomation(self, text):
        """文字列を受け取り、未設定の商品情報を登録していきます。
        また、次に必要な情報を促す文字列を返します。

        Args:
            text (str): 文字列。

        Returns:
            str: 次に必要な情報を促す文字列。
        """
        previous = self.state
        self.update_state()
        if previous == 0:
            return self.responses[self.state]
        self.store_infomation_value(text)
        if self.info['confirm'] in ('ok', 'no'):
            if self.info['confirm'] == 'ok':
                self.send_database()
                res = "登録しました。"
            else:
                res = "登録を取り消しました。"
            self.end()
            return res
        if self.state == 'confirm':
            return self.responses[self.state].format(*self.values)
        return self.responses[self.state]

    def response(self, text):
        """応答を生成し、返します。
        受け取った文字列に応じて、商品情報登録の進捗制御、返信の作成を行います。

        Args:
            text (str): ユーザーからの入力。

        Returns:
            str: AIからの応答。
        """
        res = self.add_infomation(text)
        return res

    def send_database(self):
        """完成した商品情報をデータベースに登録します。
        商品名、分量、店、支店名が同じ商品が存在する場合、今回の商品情報で更新されます。
        """
        del_data = (self.info['name'], self.info['amount'], self.info['shop'],
                    self.info['shop_branch'])
        data = tuple(self.info[key] for key in self.keys if key != 'confirm')

        sqls = [
            "delete from products where name='{}' and amount={} and shop='{}' and shop_branch='{}'"
            .format(*del_data), f"insert into products values {data}"
        ]
        for sql in sqls:
            self.cursor.execute(sql)

    def store_infomation_value(self, text):
        """文字列を受け取り、現在のstateに応じて商品情報を登録していきます。
        最後に、最新のstateに更新します。

        Args:
            text (str): stateに応じた文字列。
        """
        state = self.state
        if state == 'name':
            if text:
                self.info['name'] = text
        elif state == 'amount':
            value = self.text_to_value(text)
            if value is not None:
                self.info['amount'] = value
        elif state == 'price':
            value = self.text_to_value(text, int)
            if value is not None:
                self.info['price'] = value
        elif state == 'shop':
            if text:
                self.info['shop'] = text
        elif state == 'shop_branch':
            if text:
                if text[-2:] == '支店':
                    text = text[:-2]
                elif text[-1] == '店':
                    text = text[:-1]
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
        self.update_state()

    def update_state(self):
        """現在の商品情報の完成度に応じてstateを更新します。
        """
        if self.state == 0:
            self.state = 'name'
            return
        for key in self.keys:
            data = self.info[key]
            if not data and data is not None:
                self.state = key
                return

    @property
    def info(self):
        """商品情報を登録する辞書です。

        Returns:
            dict: 商品情報。
        """
        return self.__infomation

    @property
    def keys(self):
        """商品名, 分量, 価格, 店, 支店名の順のキータプルを返します。

        Returns:
            tuple: 商品名, 分量, 価格, 店, 支店名のキー。
        """
        return self.__keys

    @property
    def responses(self):
        """応答パターンの辞書です。

        Returns:
            dict: 応答パターン。
        """
        return self.__responses

    @property
    def values(self):
        """商品名, 分量, 価格, 店, 支店名の順のタプルを返します。

        Returns:
            tuple: 商品名, 分量, 価格, 店, 支店名。
        """
        i = self.info
        return (i['name'], i['amount'], i['price'], i['shop'],
                i['shop_branch'])


class ProductResponder(Responder):
    """商品情報を返すレスポンダです。
    データベースを参照し、単価が安い順番に並べて返します。

    商品が見つからなかった場合に商品を登録するか確認し、AddResponderを生成、保持します。
    また、AddResponderを保持している間はAddResponderとして振舞います。

    ※AddResponderの保持、振舞いは未定義です。
    今後のバージョンアップで追加します。

    Attributes
    adder (AddResponder): 商品情報を追加するレスポンダです。
    """
    def __init__(self):
        """商品情報を参照します。
        """
        super().__init__()
        self.__adder: AddResponder = None
        self.__guess = {}

    def format_products(self, rows):
        """商品情報群を受け取り、文字列として整形して返します。

        Args:
            rows (list[tuple]): 商品情報群。

        Returns:
            str: 商品情報。
        """
        text = ""
        products = []
        amount_length = 0
        price_length = 0
        for row in rows:
            name, amount, price, shop, branch = map(str, row)
            amount = str(self.text_to_value(amount))
            price = str(self.text_to_value(price))
            products.append((amount, price, shop, branch))
            if not text:
                text = f'{name}\n'
            amount_length = max((amount_length, len(amount)))
            price_length = max((price_length, len(price)))
        for product in products:
            amount, price, shop, branch = product
            values = (
                amount.center(amount_length, '　'),
                price.center(price_length, '　'),
                shop,
                branch,
            )
            text += '{}, {}: {} {}\n'.format(*values)
        return text

    def guess_product(self, text):
        """文字列を受け取り、その文字列がなるべく長く一致する商品を探し、一覧を返します。
        また、見つかった候補をguess[番号]=名前として登録していきます。
        さらに、候補が見つかった場合はstateを'guess'に変更します。

        Args:
            text (str): 商品名の一部。

        Returns:
            str or None: 候補が見つかれば、その一覧。なければNone。
        """
        base_sql = "select name from products where name ~* '{}'"
        for word in generate_words(text):
            sql = base_sql.format(word)
            print(f"sql: {sql}")  # Debug
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            print(f"rows: {rows}")  # Debug
            if rows:
                res = f'目当ての商品があれば対応する番号を入力してください。\n無ければそれ以外の文字を送信してください。\n'
                for n, name in enumerate(set(str(x[0]) for x in rows)):
                    self.guess[n] = name
                    res += f'{n}: {name}\n'
                self.state = 'guess'
                return res

    def response(self, text):
        """文字列を受け取り、商品情報を単価の安い順, 数量の少ない順でソートして返します。
        AddResponderを保持している場合はAddResponderとして振舞います。

        Args:
            text (str): 検索したい文字列。

        Returns:
            str: 検索結果。または、AddReponderとしての応答。
        """
        if self.adder is not None:
            res = self.adder.response(text)
            if self.adder.state == 'end':
                self.adder.exit()
                self.adder = None
                self.end()
            return res
        if self.state == 'guess':
            res = self.truth_product(text)
            self.end()
        elif text in ('-s', '--show'):
            res = self.show_products()
            self.end()
        else:
            res = self.retrieve(text)
            if self.state != 'guess':
                self.end()
        if not res:
            res = f"{text}が見つかりませんでした。\n登録されていないか、誤字脱字の可能性があります。"
        return res.strip()

    def retrieve(self, text):
        """データベースから商品情報を受け取り、整形して返します。

        Args:
            text (str): 商品名。

        Returns:
            str: 商品情報。
        """
        sql = f"select * from products where name='{text}' order by price/amount,amount limit 5"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        if not rows:
            return self.guess_product(text)
        return self.format_products(rows)

    def show_products(self):
        """データベースに登録されている商品名の一覧を返します。

        Returns:
            str: 商品名一覧。
        """
        sql = "select name from products order by name"
        self.cursor.execute(sql)
        return "\n".join(set(str(x[0]) for x in self.cursor.fetchall()))

    def truth_product(self, text):
        """数値変換可能な文字列を受け取り、その値がguessに存在した場合、retrieve(guess[int(text)])を返します。

        Args:
            text (str): 数値変換可能な文字列。

        Returns:
            str: 商品情報の文字列。または、終了を伝えるメッセージ。
        """
        num = Responder.text_to_value(text, int)
        if num in self.guess:
            return self.retrieve(self.guess[num])
        return "問い合わせを終了しました。"

    @property
    def adder(self):
        """商品情報を登録するレスポンダです。

        Returns:
            AddResponder or None: 商品情報を登録するレスポンダです。必要ないときはNoneです。
        """
        return self.__adder

    @property
    def guess(self):
        """商品情報が見つからなかった時の予測候補です。

        Returns:
            dict: 商品情報の予測候補。
        """
        return self.__guess
