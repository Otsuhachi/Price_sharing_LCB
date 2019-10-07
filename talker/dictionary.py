from pathlib import Path


class Dictionary:
    def __init__(self):
        self.__file = Path('talker', 'dics', 'pattern.txt')
        self.__actions = []
        self.load()

    def load(self):
        with open(self.__file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line:
                    continue
                type_, pattern, mode = (x.strip() for x in line.split('\t'))
                if type_ == 'action':
                    self.__actions.append({'pattern': pattern, 'mode': mode})

    @property
    def actions(self):
        return self.__actions


if __name__ == '__main__':
    d = Dictionary()
    for ptn in d.actions:
        print(ptn['pattern'])
