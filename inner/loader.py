import base64
import pickle
from pathlib import Path


class Loader:
    """外部ファイルから必要なデータを読み込むためのクラスです。

    このクラスはインスタンスを必要としません。

    Returns:
        str: load_uri。
        list[dict]: load_action, load_add_responses。
    """
    PATH = Path('inner', 'dics')
    PATTERN = PATH / 'pattern.txt'
    URI = PATH / 'uri.txt'

    @classmethod
    def __load(cls, mode, is_unique=False):
        """パターン定義ファイルから指定モードのデータを読み込みます。
        is_uniqueを指定すると、[{pattern: status}, {...}, ...]となります。
        標準では[{'pattern': pattern, 'status': status}, {...}, ...]となります。

        Args:
            mode (str): 読み込むパターン名。
            is_unique (bool, optional): リストに格納される辞書の形式が固有の物になります。

        Returns:
            list[dict]: パターン定義データ。
        """
        data = []
        with open(cls.PATTERN, 'r', encoding='utf-8') as f:
            for line in f:
                if not line:
                    continue
                type_, pattern, status = (x.strip() for x in line.split('\t'))
                if type_ == mode:
                    status = str(status).replace('\\n', '\n')
                    if is_unique:
                        data.append({pattern: status})
                    else:
                        data.append({'pattern': pattern, 'status': status})
        return data

    @classmethod
    def load_action(cls):
        """AIの行動を定義する辞書オブジェクトが纏められたリストを読み込みます。

        Returns:
            list[dict]: AIの行動を定義する辞書オブジェクトが纏められたリスト。
        """
        return cls.__load('action')

    @classmethod
    def load_add_responses(cls):
        """AddResponder用の定義群を読み込みます。

        Returns:
            list[dict]: AddResponder用の定義群。
        """
        return cls.__load('add_responses', True)

    @classmethod
    def load_uri(cls):
        """データベースに接続するための情報を読み込みます。

        Returns:
            str: データベースに接続するための情報。
        """
        with open(cls.URI, 'r', encoding='utf-8') as f:
            return pickle.loads(base64.b64decode(f.read()))


if __name__ == '__main__':
    print("This module is not script file.")
