"""
In a same ItemSet, items with different lookahead set should be merged into one item.
"""

import itertools
import debug

from collections import deque, defaultdict

import LRParser
import LR0
import LL1


class Item(LR0.Item):

    def __init__(self, prod, pos, lookahead):
        assert lookahead
        super(Item, self).__init__(prod , pos)
        self.lookahead = frozenset(lookahead)

    def __key_data(self):
        return self.prod, self.pos, self.lookahead

    def __str__(self):
        return '%s, %s' % (LR0.Item.__str__(self), '/'.join(map(str, self.lookahead)))

    def rear(self):
        """

        :return:
        """

        return self.prod[self.pos+1:]


class Operation(LR0.Operation, LL1.Operation):
    """
    Build LR(1) item set.
    """

    def pending(self, item):
        symbols = item.rear()

        lookahead = self.first(seq=symbols)

        if self.derive_epsilon(seq=symbols):
            lookahead |= item.lookahead

        productions = getattr(item.expect(), 'productions', ())

        return map(lambda prod: Item(prod, 0, lookahead), productions)

    def advance(self, item):

        return Item(item.prod, item.pos+1, item.lookahead)

    def eclosure(self, *items, iterable=()):
        """
        Perform the epsilon operation.

        :param items:
        :param iterable:
        :return:
        """

        # queue consist of items
        queue = deque(itertools.chain(items, iterable))
        # use the (prod, pos) as key, set of symbols as value
        seen = defaultdict(set)

        while queue:
            curr = queue.popleft()
            # Merge different set of symbols with the same (prod, pos)
            seen[curr.raw_tuple()] |= curr.lookahead

            for next in self.pending(curr):

                known = seen.get(next.raw_tuple(), None)

                if not known or not known.issuperset(next.lookahead):
                    queue.append(next)

        return LR0.ItemSet(map(lambda kv: Item(*kv[0], kv[1]), seen.items()))


class Parser(LRParser.LRParser):

    def construct(self, aug_gram):

        op = Operation()
        start = op.eclosure(Item(aug_gram.START_PROD, 0, {aug_gram.END}))
        states = {start}

        que = deque(iterable=(start,))
        while que:

            curr = que.popleft()
            states.add(curr)

            seen = set()  # Record the symbols checked following dot notation in one ItemSet

            for item in curr:

                symbol = item.expect()

                if not symbol:
                    # The item that leads to accepted state may be grouped together with other items.
                    # That means a combination such as {S->E@#, E->E@+T, E->E@-T} is also possible.

                    if item.prod == aug_gram.START_PROD:  # For the accepted state
                        self.setaction(curr, aug_gram.END, self.accept)
                    else:
                        for symbol in item.lookahead:
                            self.setaction(curr, symbol, self.reduce, item.prod)

                elif symbol not in seen:

                    seen.add(symbol)
                    next = op.goto(curr, symbol)

                    if next not in states:
                        states.add(next)
                        que.append(next)  # Append the next state to the queue

                    if hasattr(symbol, 'productions'):
                        self.setgoto(curr, symbol, next)  # For terminals,
                    else:
                        self.setaction(curr, symbol, self.shift, next)  # For non-terminals,

        return start


@debug.log_attr(msg='MAIN', log_obj=True)
def main():
    filename = './test-input/test-LR1-input_RE.txt'
    g = LRParser.AugmentedGrammarBuilder(filename=filename).build()
    parser = Parser(g)

    inputs = ['a(1a|2)+', '[ab]([ab]|[12])*', '[12ab]a+(a|b)']
    passed = 0

    for index, string in enumerate(inputs):

        symbols = [g.T[c] for c in string]
        symbols.append(g.END)

        try:
            msg, no = parser.parse(symbols)
            if no == 0:
                passed += 1
        except Exception as e:
            print('-----ERROR-----Test: %d-----%s' % (index, repr(e)))

    return 'Passed %d test.' % passed

if __name__ == '__main__':
    main()
