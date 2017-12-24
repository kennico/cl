import debug
import LRParser

from collections import deque
from itertools import chain

DOT = '@'


class Item(object):

    def __init__(self, prod, pos):
        self.prod = prod
        self.pos = pos

    def expect(self):
        """Return the symbolize after the dot notation"""

        return self.prod[self.pos] if self.pos < len(self.prod) else None

    def __key_data(self):
        """

        :return: object to be used in __hash__ and __eq__
        """

        return self.raw_tuple()

    def raw_tuple(self):
        """

        :return: (prod, pos)
        """

        return self.prod, self.pos

    def __str__(self):

        ss = [str(sym) for sym in self.prod]
        ss.insert(self.pos, DOT)
        return '%s->%s' % (self.prod.head, ''.join(ss))

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.__str__())

    # Both __hash__ and __eq__ are necessary for set
    def __hash__(self):
        return hash(self.__key_data())

    def __eq__(self, other):
        return isinstance(other, Item) and self.__key_data() == other.__key_data()

    def __ne__(self, other):
        return not self.__eq__(other)


class ItemSet(object):
    """
    Immutable item set.
    """

    # TODO Shall I make it a subclass of frozenset?
    def __init__(self, iterable):
        """

        :param iterable:
        """

        self.items = frozenset(iterable)
        #     chain(map(lambda args: item_class(*args), args_list), iterable)
        # )

    def __hash__(self):
        """
        The hash value depends on self.items
        :return:
        """

        return hash(self.items)

    def __eq__(self, other):
        """
        This should be provided along with self.__hash__
        :param other:
        :return:
        """
        if isinstance(other, ItemSet):
            return self.items == other.items
        else:
            return False

    def __contains__(self, item):
        return item in self.items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return self.items.__len__()


class Operation(object):
    """
    Build LR(0) item set.
    """

    def pending(self, item):
        """
        Construct a collection of items by placing the dot notation at the
        beginning of every production which starts with item.expect().

        If B->b|c|d, calling on A->a@B returns {B->@b, B->@c, B->@d}.

        :param item:
        :return: the items constructed DIRECTLY from the non-terminal
        """

        return [Item(prod, 0) for prod in getattr(item.expect(), 'productions', ())]

    def advance(self, item):
        """
        Return a new item where its dot notation is advanced one step.
        Calling on B->@bb returns B->b@b

        :param item:
        :return: item
        """

        return item.expect() and Item(item.prod, item.pos + 1)

    def eclosure(self, *items, iterable=()):
        """
        Perform the epsilon operation.

        :param items:
        :param iterable:
        :return:
        """
        queue = deque(chain(items, iterable))

        seen = set()
        empty = ()

        while queue:
            item = queue.popleft()
            seen.add(item)

            for next in (self.pending(item) or empty):
                if next not in seen:
                    queue.append(next)

        return ItemSet(seen)

    def goto(self, src, sym):
        """
        Perform the goto operation starting from an item set through a given symbol

        :param src: current state
        :param sym: symbol
        :return: item set
        """

        return self.eclosure(iterable=[self.advance(t) for t in src if t.expect() == sym])


class Parser(LRParser.LRParser):

    def construct(self, aug_gram):

        op = Operation()
        start = op.eclosure(Item(aug_gram.START_PROD, 0))
        states = set()

        que = deque(iterable=(start,))

        while que:

            curr = que.popleft()
            states.add(curr)

            seen = set()

            for item in curr:

                symbol = item.expect()

                if not symbol:
                    # The item that leads to accepted state may be grouped together with other items.
                    # That means a combination such as {S->E@#, E->E@+T, E->E@-T} is also possible.

                    if item.prod == aug_gram.START_PROD:  # For the accepted state
                        self.setaction(curr, aug_gram.END, self.accept)
                    else:
                        for symbol in aug_gram.terminals():
                            self.setaction(curr, symbol, self.reduce, item.prod)

                elif symbol not in seen:

                    seen.add(symbol)
                    next = op.goto(curr, symbol)

                    if next not in states:
                        que.append(next)  # Append the next state to the queue

                    if hasattr(symbol, 'productions'):
                        self.setgoto(curr, symbol, next)  # For terminals,
                    else:
                        self.setaction(curr, symbol, self.shift, next) # For non-terminals,

        return start


@debug.log_attr(msg='MAIN')
def main():

    with open('test-input/test-LR0.txt') as f:
        inputs = [line.split() for line in f]

    passed = 0
    for index, arg in enumerate(inputs):
        fn, *string = arg

        print('Test %d:' % index)

        g = LRParser.AugmentedGrammarBuilder(filename=fn).build()
        parser = Parser(g)

        symbols = [g.T[c] for c in string]
        symbols.append(g.END)

        msg, no = parser.parse(symbols)
        if no == 0:
            passed += 1

    print('Passed %d.' % passed)


if __name__ == '__main__':
    main()
