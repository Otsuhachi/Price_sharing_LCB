from pathlib import Path


class Dictionary:
    """AIの応答パターンを管理するファイルにアクセスするためのクラスです。


    Attributes:
        actions (list[dict]): AIの行動の定義群です。
        add_responses (list[dict]): AddResponder用の定義群です。
        todo (list[dict]): 実装予定の定義群です。
    """
    def __init__(self):
        """定義ファイルを読み込みます。

        読み込んだ定義ファイルを取得する場合は目的の種類のプロパティにアクセスしてください。

        Examples:
            >>> from dictionary import Dictionary
            >>> dic = Dictionary()
            >>> dic.actions
            [{'pattern': '^(登録|追加|とうろく|ついか|add)', 'status': 'add'}]
        """
        self.__file = Path('talker', 'dics', 'pattern.txt')
        self.__actions = []
        self.__add_responses = []
        self.__todo = []
        self.__load()

    def __load(self):
        """このメソッドは自動実行専用です。
        """
        with open(self.__file, 'r', encoding='utf-8') as f:
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

    @property
    def actions(self):
        """AIの行動を定義する辞書オブジェクトが纏められたリストです。

        Returns:
            list[dict]: AIの行動を定義する辞書オブジェクトが纏められたリスト。
        """
        return self.__actions

    @property
    def add_responses(self):
        return self.__add_responses

    @property
    def todo(self):
        """AIの応答パターンに追加するかもしれない反応の定義群です。

        Returns:
            list[dict]: AIの応答パターンに追加するかもしれない反応の定義群。
        """
        return self.__todo


if __name__ == '__main__':
    print("This module is not script file.")
