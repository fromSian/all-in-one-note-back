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
