class Debug(object):

    @staticmethod
    def print(**kwargs):
        '''
        Print names and results of method calls on the return object of a function
        '''
        names = kwargs.pop('names', [])
        meths = kwargs.pop('meths', [])

        def decorate(func):
            def unnamed(*args, **kwargs):
                obj = func(*args, **kwargs)
                for name in names:
                    try:
                        attr = getattr(obj, name)
                        print('Name -%s- : %s' % (name, repr(attr)))
                    except Exception as e:
                        print(e)
                for name in meths:
                    try:
                        meth = getattr(obj, name)
                        print('Method -%s- called: %s' % (name, repr(meth())))
                    except Exception as e:
                        print(repr(e))
                return obj

            return unnamed

        return decorate
