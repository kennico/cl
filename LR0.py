import debug
import LRParser

from collections import deque
from itertools import chain

DOT = '@'


class Item(object):

    def __init__(self, prod, pos):
        self.prod = prod
        self.pos = pos

    def expected(self):
        """Return the symbolize after the dot notation"""

        return self.prod[self.pos] if self.pos < len(self.prod) else None

    def __str__(self):
        ss = [str(sym) for sym in self.prod]
        ss.insert(self.pos, DOT)
        return '%s->%s' % (self.prod.head, ''.join(ss))

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.__str__())

    # Both __hash__ and __eq__ are necessary for set
    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.prod == other.prod and self.pos == other.pos
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class ItemSet(object):
    """
    Immutable item set.
    """

    # TODO Shall I make it a subclass of frozenset?
    def __init__(self, iterable):
        """
        Construct the LR item set.

        :param iterable:
        """

        self.items = frozenset(iterable)

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

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return self.items.__len__()


class Operation(object):
    """
    Build LR(0) item set.
    """

    # TODO Is it necessary to return None when dot notation has reached the end?
    def pending(self, item):
        """
        Construct a collection of items by placing the dot notation at the
        beginning of every production which starts with item.expected().

        If B->b|c|d, calling on A->a@B returns {B->@b, B->@c, B->@d}.

        :param item:
        :return: the items constructed DIRECTLY from the non-terminal
        """

        return [Item(prod, 0) for prod in getattr(item.expected(), 'productions', ())]

    def advance(self, item):
        """
        Return a new item where its dot notation is advanced one step.
        Calling on B->@bb returns B->b@b

        :param item:
        :return: item
        """
        return item.expected() and Item(item.prod, item.pos + 1)

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

        return self.eclosure(iterable=[self.advance(t) for t in src if t.expected() == sym])


class Parser(LRParser.LRParser):

    def construct(self, aug_gram):

        action = {}
        goto = {}

        op = Operation()
        start = op.eclosure(Item(aug_gram.START_PROD, 0))
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
                    # The item that leads to accepted state may be grouped together with other items.
                    # That means a combination such as {S->E@#, E->E@+T, E->E@-T} is also possible.

                    if item.prod.head == aug_gram.START:  # For the accepted state
                        action[(curr, aug_gram.END)] = (self.accept,)
                    else:
                        # Reduce/Reduce or Shift/Reduce conflict found.
                        if len(curr) > 1:
                            raise LRParser.ParseError('Conflict found.', -1)
                        for sym in aug_gram.terminals():
                            action[(curr, sym)] = (self.reduce, item.prod)

        return start, action, goto


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

    return 'Passed %d.' % passed


if __name__ == '__main__':
    main()
