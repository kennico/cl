import debug

import LRParser
import LR0
import LL1

from collections import deque


class Item(LR0.Item):

    def __init__(self, prod, pos, lookahead):
        super(Item, self).__init__(prod, pos)
        self.lookahead = lookahead

    def __str__(self):
        return '%s, %s' % (LR0.Item.__str__(self), '/'.join(map(str, self.lookahead)))

    def rear(self):
        """
        Calling on A->a@BCDe returns symbols [CDe].

        If the dot notation has reached the end, an empty list will be returned.

        :return: symbols following the symbol one next to the dot notation
        """

        return self.prod[self.pos+1:]

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if isinstance(other, Item):
            return LR0.Item.__eq__(self, other) and self.lookahead == other.lookahead
        else:
            return False


class Operation(LR0.Operation):
    """
    Build LR(1) item set.
    """

    def __init__(self, grammar):
        self.LL1 = LL1.Operation(grammar)

    def pending(self, item):
        symbols = item.rear()
        lookahead = self.LL1.first(seq=symbols)

        if self.LL1.derive_epsilon(seq=symbols):
            lookahead |= item.lookahead

        productions = getattr(item.expected(), 'productions', ())
        return [Item(prod, 0, lookahead) for prod in productions]

    pending.__doc__ = LR0.Operation.pending.__doc__

    def advance(self, item):
        return Item(item.prod, item.pos+1, item.lookahead)
    advance.__doc__ = LR0.Operation.advance.__doc__


class Parser(LR0.Parser):

    def construct(self, aug_gram):

        action = {}
        goto = {}

        op = Operation(aug_gram)
        start = op.eclosure(Item(aug_gram.START_PROD, 0, {aug_gram.END}))
        states = {start}

        que = deque(iterable=(start,))
        while que:
            curr = que.popleft()

            for item in curr:
                if item.expected():
                    sym = item.expected()
                    next = op.goto(curr, sym)

                    if next not in states:
                        states.add(next)
                        que.append(next)  # Append the next state to the queue

                    if hasattr(sym, 'productions'):
                        goto[(curr, sym)] = next  # For terminals,
                    else:
                        action[(curr, sym)] = (self.shift, next)  # For non-terminals,
                else:

                    if item.prod.head == aug_gram.START:  # For the accepted state
                        action[(curr, aug_gram.END)] = (self.accept,)
                    else:
                        for sym in item.lookahead:
                            action[(curr, sym)] = (self.reduce, item.prod)
        self.states = states
        return start, action, goto


@debug.log_attr(msg='MAIN')
def main():

    with open('test-input/test-LR1.txt') as f:
        inputs = [line.split() for line in f.read().splitlines()]

    passed = 0
    for index, arg in enumerate(inputs):
        fn, *string = arg

        print('Test %d:' % index)

        g = LRParser.AugmentedGrammarBuilder(filename=fn).build()
        parser = Parser(g)

        symbols = [g.T[c] for c in string]
        symbols.append(g.END)
        try:
            msg, no = parser.parse(symbols)
            if no == 0:
                passed += 1
        except Exception as e:
            print('-----ERROR-----Test: %d-----%s' % (index, repr(e)))

    return 'Passed %d.' % passed


if __name__ == '__main__':
    main()
