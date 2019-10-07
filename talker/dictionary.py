class Dictionary:
    def __init__(self):
        dics = 'talker/dics/'
        self.__dics = {
            'random': f'{dics}random.txt',
            'pattern': f'{dics}pattern.txt'
        }

    def get_responses(self, dict_name):
        """応答定義ファイルから応答リストを生成し、返します。
        この処理の後、さらに加工が必要な場合は該当propertyで処理を行ってください。

        Args:
            dict_name (str): 読み込む定義ファイルの名前。

        Returns:
            list[str]: 応答リスト。
        """
        dict_name = dict_name.lower()
        dic = self.__dics[dict_name]
        with open(dic, 'r', encoding='utf-8') as f:
            return [x.strip() for x in map(lambda x: x.strip(), f) if x]

    @property
    def random(self):
        """RandomResponder用の応答リストです。

        Returns:
            list[str]: RandomResponder用の応答リスト。
        """
        return self.get_responses('Random')

    @property
    def pattern(self):
        """PatternResponder用の応答リストです。

        Returns:
            list[str]: PatternResponder用の応答リスト。
        """
        data = self.get_responses('Pattern')
        return [Dictionary.make_pattern(x) for x in data]

    @staticmethod
    def make_pattern(line):
        """受け取った文字列から辞書オブジェクトを生成し、返します。
        タブ文字で{key:values}に分けられます。
        また、valuesは"|"で分割された文字列のリストになります。

        Args:
            line (str): 辞書化する特定形式の文字列。

        Returns:
            dict{str:list[str]}: 辞書。
        """
        pattern, phrases = line.split('\t')
        if pattern and phrases:
            return {'pattern': pattern, 'phrases': phrases.split('|')}
