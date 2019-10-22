def generate_words(text):
    """受け取った文字列を1文字ずつ減らして返します。

    Args:
        text (str): 文字列。


    Examples:
        >>> list(generate_words("Examples"))
        ['Examples', 'Example', 'Exampl', 'Examp', 'Exam', 'Exa', 'Ex', 'E']
    """
    len_ = len(text)
    for i in range(len_):
        yield text[0:len_ - i]


def text_to_value(text, mode='both'):
    """文字列を数値変換し、返します。

    modeで変換結果が変わります。
    modeに指定できる引数は[float, int, 'both']のいずれかで、それ以外を与えた場合は'both'になります。

    Examples:
        Case1:
            >>> a='2'
            >>> text_to_value(a)
            2
            >>> text_to_value(a, int)
            2
            >>> text_to_value(a, float)
            2.0
            >>> str(text_to_value('a'))
            'None'

        Case2:
            >>> a='2.3'
            >>> text_to_value(a)
            2.3
            >>> text_to_value(a, int)
            2
            >>> text_to_value(a, float)
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


if __name__ == '__main__':
    print(list(generate_words("Examples")))
