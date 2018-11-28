def isiterable(o):
    try:
        list(o)
        return True
    except TypeError:
        return False
