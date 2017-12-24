import itertools

import debug


class Operation(object):

    def __init__(self): # TODO Implement FIRST and FOLLOW
        self._first = {}
        self._follow = {}
        self._derive_epsilon = {}

    # TODO this impl returns True on derive_epsilon(seq=())
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
                        #
                        # TODO What if temp is an empty list?
                        # A->ABC|B while A, B and C are waiting
                        #
                        temp = [subsym for subsym in prod if subsym not in waiting]
                        if all(map(recur, temp)):
                            _de[sym] = True
                            break
                    if sym not in _de:  # Assertion: if sym in _de, _de[sym] must be true
                        _de[sym] = False

                    waiting.discard(sym)  # Remember to remove it from the waiting set
                else:
                    _de[sym] = False  # For terminal it's always False

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
        _fst = self._first

        def recur(sym):
            """
            Recursively calculate FIRST(α)

            :param sym: α
            :return: a set of symbols
            """
            if sym not in _fst:

                productions = getattr(sym, 'productions', None)

                if productions:  # Non-terminal
                    _fst[sym] = set()

                    for prod in productions:
                        for subsym in prod:

                            _fst[sym] |= recur(subsym)

                            if not self.derive_epsilon(subsym):
                                break

                else:  # Terminal
                    _fst[sym] = {sym}

            return _fst[sym]

        result = set()
        for sym in itertools.chain(symbols, seq):

            result |= recur(sym)

            if not self.derive_epsilon(sym):
                break

        return result

    # TODO stub method
    def follow(self, *symbols, seq=()):
        raise NotImplementedError


@debug.log_attr(msg='main', log_obj=True)
def main():
    from grammar import GrammarBuilder

    with open('test-input/test-LL1.txt') as f:
        inputs = [line.split() for line in f]

    for index, arg in enumerate(inputs):

        fn, *_ = arg

        print('Test %d:' % index)
        g = GrammarBuilder(filename=fn).build()
        op = Operation()

        for nt in g.nterminals():
            print(nt)
            op.derive_epsilon(nt)

        for nt in g.nterminals():
            print(nt)
            op.first(nt)

    return 'Main finished.'


if __name__ == '__main__':
    main()

