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


if __name__ == '__main__':
    print(list(generate_words("Examples")))
