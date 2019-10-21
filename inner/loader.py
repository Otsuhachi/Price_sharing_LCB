from pathlib import Path
import pickle
import base64


class Loader:
    """AIの応答パターンを管理するファイルにアクセスするためのクラスです。


    Attributes:
        actions (list[dict]): AIの行動の定義群です。
        add_responses (list[dict]): AddResponder用の定義群です。
        todo (list[dict]): 実装予定の定義群です。
        uri (str): Postgresqlに接続する情報です。
    """
    def __init__(self):
        """定義ファイルを読み込みます。

        読み込んだ定義ファイルを取得する場合は目的の種類のプロパティにアクセスしてください。

        Examples:
            >>> from loader import Loader
            >>> loader = Loader()
            >>> loader.actions
            [{'pattern': '^(登録|追加|とうろく|ついか|add)', 'status': 'add'}]
        """
        self.__path = Path('inner', 'dics')
        self.__pattern_file = self.__path / 'pattern.txt'
        self.__db_file = self.__path / 'db.txt'
        self.__actions = []
        self.__add_responses = []
        self.__todo = []
        self.__load()

    def __load(self):
        """このメソッドは自動実行専用です。
        """
        with open(self.__pattern_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line:
                    continue
                type_, pattern, status = (x.strip() for x in line.split('\t'))
                if type_ == 'action':
                    self.__actions.append({
                        'pattern': pattern,
                        'status': status
                    })
                elif type_ == 'todo':
                    self.__todo.append({'pattern': pattern, 'status': status})
                elif type_ == 'add_responses':
                    status = str(status).replace('\\n', '\n')
                    self.__add_responses.append({pattern: status})
        with open(self.__db_file, 'r', encoding='utf-8') as f:
            self.__uri = pickle.loads(base64.b64decode(f.read()))

    @property
    def actions(self):
        """AIの行動を定義する辞書オブジェクトが纏められたリストです。

        Returns:
            list[dict]: AIの行動を定義する辞書オブジェクトが纏められたリスト。
        """
        return self.__actions

    @property
    def add_responses(self):
        """AddResponder用の定義群です。

        Returns:
            list[dict]: AddResponder用の定義群。
        """
        return self.__add_responses

    @property
    def todo(self):
        """AIの応答パターンに追加するかもしれない反応の定義群です。

        Returns:
            list[dict]: AIの応答パターンに追加するかもしれない反応の定義群。
        """
        return self.__todo

    @property
    def uri(self):
        """データベースに接続するための情報です。

        Returns:
            str: データベースに接続するための情報。
        """
        return self.__uri


if __name__ == '__main__':
    print("This module is not script file.")
