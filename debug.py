from collections import defaultdict


def log_attr(*names, msg=''):
    """
    Log attributes of the return object of the decorated function.
    """

    def decorate(func):
        def unnamed(*args, **kwargs):
            obj = func(*args, **kwargs)

            print('Message : ' + msg)
            print('Return -Object- : ' + repr(obj))

            for name in names:
                try:
                    attr = getattr(obj, name)
                    print('Name -%s- : %s' % (name, repr(attr)))
                except Exception as e:
                    print(repr(e))

            return obj

        unnamed.__name__ = func.__name__
        unnamed.__doc__ = func.__doc__

        return unnamed
    return decorate


