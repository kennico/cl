import grammar
import debug

from collections import deque


DOT_NOTATION = '@'


class Item(object):

    def __init__(self, prod, pos):
        self.prod = prod
        self.pos = pos

    def expected(self):
        """Return the symbolize after the dot notation"""

        return self.prod[self.pos] if self.pos < len(self.prod) else None

    def __str__(self):
        ss = [str(sym) for sym in self.prod]
        ss.insert(self.pos, DOT_NOTATION)
        return '%s->%s' % (self.prod.head, ''.join(ss))

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.__str__())

    # Both __hash__ and __eq__ are necessary for set
    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        if isinstance(other, Item):
            return (self.prod == other.prod) and (self.pos == other.pos)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class ItemSet(object):
    """Immutable item set"""
    items = None

    def pending(self):
        return {t.expected() for t in self if t.expected()}

    def __hash__(self):
        return hash(self.items)

    def __eq__(self, other):
        if isinstance(other, ItemSet):
            return self.items == other.items
        else:
            return False

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return self.items.__len__()


class _Closure(ItemSet):
    """
    Perform the e-closure operation on the given items in a BFS way.
    """

    def __init__(self, *items):
        queue = deque(items)
        result = set()
        empty = ()

        while queue:
            front = queue.popleft()
            result.add(front)

            for prod in getattr(front.expected(), 'productions', empty):
                temp = Item(prod, 0)
                if temp not in result:
                    queue.append(temp)

        self.items = frozenset(result)


def closure(*items, **kwargs):
    """
    Calculate the ItemSet from different manners.

    Given multiple items:

    >>> item1 = ...
    >>> item2 = ...
    >>> item3 = ...
    >>> itemset = closure(item1, item2, item3)

    Given a non-terminal by placing the dot notation before it:

    >>> nt = ...
    >>> itemset = closure(nt=nt)

    Given an ItemSet and a symbolize in order to perform the goto function:

    >>> src = ...
    >>> a = ...
    >>> itemset = closure(src=src, sym=a)
    :param items:
    :param kwargs:
    :return:
    """

    nt = kwargs.get('nt', None)
    nt_items = tuple(Item(prod, 0) for prod in nt.productions) if nt else ()

    increase = lambda item: item.expected() and Item(item.prod, item.pos+1)
    src = kwargs.get('src', None)
    sym = kwargs.get('sym', None)
    gt_items = tuple(increase(t) for t in src if t.expected() == sym) if src and sym else ()

    return _Closure(*(items + nt_items + gt_items))


class ParseError(Exception):
    pass


class ParseFinish(Exception):
    pass


class LR0Parser(object):
    """
    Apply to an augmented grammar which has only one production starts with the START symbol
    """

    def __init__(self, grammar):

        if len(grammar.START.productions) != 1:
            raise ParseError('An augmented grammar is required.')

        self.grammar = grammar
        self.cal_collections()

    def cal_collections(self):
        """
        Calculate canonical LR(0) collections in a BFS way.
        :return:
        """
        action = {}
        goto = {}

        first = closure(nt=self.grammar.START)
        known = {first}

        que = deque(iterable=(first,))
        while que:
            curr = que.popleft()

            for item in curr:
                if item.expected():
                    sym = item.expected()
                    next = closure(src=curr, sym=sym)

                    if next not in known:
                        known.add(next)
                        que.append(next)  # Append the next state to the queue

                    if hasattr(sym, 'productions'):
                        goto[(curr, sym)] = next  # For terminals,
                    else:
                        action[(curr, sym)] = (self.shift, next)  # For non-terminals,
                else:
                    # The item that leads to accepted state may be grouped with other items.
                    # That means a combination such as {S->E@#, E->E@+T, E->E@-T} is also possible.

                    if item.prod.head == self.grammar.START:  # For the accepted state
                        action[(curr, self.grammar.END)] = (self.accept,)
                    else:
                        for sym in self.grammar.terminals():
                            action[(curr, sym)] = (self.reduce, item.prod)

        self.collections = known
        self.first = first
        self.goto = goto
        self.action = action

    def accept(self):
        raise ParseFinish('Accepted.')

    @debug.log_attr(msg='SHIFT')
    def shift(self, state):
        """
        Shift a symbolize from self.input and push the state onto self.stack

        :param state:
        :return:
        """
        sym = self.input.popleft()
        self.stack.append((state, sym))

        # TODO Return is of no use here but for debugging
        return sym

    @debug.log_attr(msg='REDUCE')
    def reduce(self, prod):
        """
        Reduce the prod.body on the top of self.stack to prod.head

        :param prod: a Production object used in the reduction
        :return:
        """

        stack = self.stack[:-len(prod)]     # Pop states and symbols from the stack
        curr, _ = stack[-1]

        try:
            next = self.goto[(curr, prod.head)]
        except KeyError:
            raise ParseError('No such transition.')

        stack.append((next, prod.head))
        self.stack = stack      # Remember to assgin self.stack stack

        # TODO Return is of no use here but for debugging
        return prod

    def parse(self, symbols):
        self.input = deque(symbols)
        self.input.append(self.grammar.END)
        self.stack = [(self.first, self.grammar.END)]

        while True:
            try:
                curr, _ = self.stack[-1]
                sym = self.input[0]

                action = self.action.get((curr, sym), None)
                if not action:
                    raise ParseError('No such action.')

                meth = action[0]
                meth(*action[1:])

            except (ParseFinish, ParseError) as e:
                print(repr(e))
                break


def test_LR0Parser():

    with open('input/test-LR0.txt') as f:
        inputs = [line.split() for line in f]

    for index, arg in enumerate(inputs):
        filename, *string = arg

        print('Test %d:' % index)

        g = grammar.Builder(filename=filename).build()
        parser = LR0Parser(g)
        parser.parse([g.T[c] for c in string])


if __name__ == '__main__':
    test_LR0Parser()
