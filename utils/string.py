def to_readable_str(value):
    """
    convert number/list/dict to readable string
    :param string:
    :return:
    """
    print(value, type(value))
    if isinstance(value, list):
        return ".".join(v for v in value)
    elif isinstance(value, dict):
        return ".".join("{0}: {1}".format(key, v) for (key, v) in value.items())
    else:
        return str(value)


import random, string


def random_word(length):
    letters = string.ascii_lowercase
    numbers = string.digits
    return "".join(random.choice(letters + numbers) for i in range(length))
