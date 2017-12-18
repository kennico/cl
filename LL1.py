import itertools

import debug


class Operation(object):

    def __init__(self, grammar): # TODO Implement FIRST and FOLLOW
        self._first = {}
        self._follow = {}
        self._derive_epsilon = {}

    #@debug.log_attr(msg='derive_epsilon')
    def derive_epsilon(self, *symbols, seq=()):
        """
        Check if the given symbols can derive epsilon.

        :param symbols:
        :return: True when the all symbols in a given sequence derive epsilon
        """

        _de = self._derive_epsilon
        waiting = set()  # Non-terminals waiting to be checked.

        def recur(sym):
            """
            Recursively check if a symbol can derive epsilon.

            :param sym:
            :return: True when the all symbols in a given sequence derive epsilon
            """

            if sym not in _de:
                productions = getattr(sym, 'productions', None)

                if productions:  # Non-terminal
                    waiting.add(sym)  # In case of recursion

                    for prod in productions:
                        temp = [subsym for subsym in prod if subsym not in waiting]
                        if all(map(recur, temp)):
                            _de[sym] = True
                            break
                    if sym not in _de:  # If sym in _de, _de must be true
                        _de[sym] = False

                    waiting.discard(sym)  # Remember to remove symbol from waiting set
                else:
                    _de[sym] = False  # For a terminal it is always False

            return _de[sym]
        assert not waiting  # TODO Assertion
        return all([recur(sym) for sym in itertools.chain(symbols, seq)])

    #@debug.log_attr(msg='first')
    def first(self, *symbols, seq=()):
        """
        Performt the FIRST operation -> FIRST(α)

        :param symbols: a sequence of grammar symbols
        :return: a set of symbols
        """
        _first = self._first

        def recur(sym):
            """
            Recursively calculate FIRST(α)

            :param sym: α
            :return: a set of symbols
            """
            if sym not in _first:

                productions = getattr(sym, 'productions', None)

                if productions:  # Non-terminal
                    _first[sym] = set()

                    for prod in productions:
                        for subsym in prod:

                            _first[sym] |= recur(subsym)

                            if not self.derive_epsilon(subsym):
                                break

                else:  # Terminal
                    _first[sym] = {sym}

            return _first[sym]

        result = set()
        for sym in itertools.chain(symbols, seq):
            result |= recur(sym)

        return result

    def follow(self, *symbols, iterable=()):
        raise NotImplementedError


@debug.log_attr(msg='main')
def main():
    from grammar import GrammarBuilder

    with open('test-input/test-LL1.txt') as f:
        inputs = [line.split() for line in f]

    for index, arg in enumerate(inputs):

        fn, *_ = arg

        print('Test %d:' % index)
        g = GrammarBuilder(filename=fn).build()
        op = Operation(g)

        for nt in g.nterminals():
            print(nt)
            op.derive_epsilon(nt)

        for nt in g.nterminals():
            print(nt)
            op.first(nt)

    return 'Main finished.'



if __name__ == '__main__':
    main()

