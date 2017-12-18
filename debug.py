from collections import defaultdict
from functools import wraps


def log_attr(names=(), msg=''):
    """
    Log attributes of the return object of the decorated function.
    """

    def decorate(func):
        def unnamed(*args, **kwargs):

            print('MESSAGE: ' + msg)

            obj = func(*args, **kwargs)
            for name in names:
                try:
                    attr = getattr(obj, name)
                    print('ATTRIBUTE -%s- : %s' % (name, repr(attr)))
                except Exception as e:
                    print(repr(e))

            return obj

        return unnamed
    return decorate


def log_param(names=(), msg=''):
    """
    Log attributes of the return object of the decorated function.
    """

    def decorator(func):
        """
        Function decorator logging entry + exit and parameters of functions.

        Entry and exit as logging.info, parameters as logging.DEBUG.
        https://stackoverflow.com/questions/6200270/decorator-to-print-function-call-details-parameters-names-and-effective-values+&cd=1&hl=zh-CN&ct=clnk&gl=cn
        """

        @wraps(func)
        def wrapper(*fn_args, **fn_kwargs):
            if msg:
                print('MESSAGE: ' + msg)

            # get function params (args and kwargs)
            arg_names = func.__code__.co_varnames

            params = dict(zip(arg_names, fn_args))
            params.update(fn_kwargs)

            for k in names:
                if k in params:
                    print(str(params[k]))

            # Execute wrapped (decorated) function:
            out = func(*fn_args, **fn_kwargs)

            return out

        return wrapper

    return decorator