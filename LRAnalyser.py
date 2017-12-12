import elements
import utils

from collections import deque


class Item(object):
    def __init__(self, prod, pos):
        self.prod = prod
        self.pos = pos

    def pending(self):
        """Return the symbol after the dot notation"""
        return self.prod[self.pos] if self.pos < len(self.prod) else None

    def shift(self):
        # TODO Handle the case where A->e generates only A->@
        return Item(self.prod, self.pos+1)

    def __str__(self):
        ss = [str(sym) for sym in self.prod]
        ss.insert(self.pos, '@')
        return '%s->%s' % (self.prod.head, ''.join(ss))

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.__str__())

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
    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join(str(item) for item in self.items))

    def pending_symbols(self):
        return {t.pending() for t in self.items if t.pending()}


class EClosure(ItemSet):
    def __init__(self, *items):
        queue = deque(items)
        result = set()
        empty = ()

        while queue:
            front = queue.popleft()
            result.add(front)

            for prod in getattr(front.pending(), 'productions', empty):
                temp = Item(prod, 0)
                if temp not in result:
                    queue.append(temp)

        self.items = result


class Goto(EClosure):
    def __init__(self, itemset, symbol):
        temp = [t.shift() for t in itemset.items if symbol == t.pending()]
        super(Goto, self).__init__(*temp)


class LR0Analyser(object):
    def __init__(self, grammar):
        self.canonical = {}
        self.grammar = grammar
        self.cal_collection()

    def cal_collection(self):
        # TODO Calculate the DFA
        collection = set()
        queue = deque()
        NT = self.grammar.T['(']

        st = self.grammar.START
        self.debug_closure = EClosure(Item(st.productions[0], 0))
        self.debug_goto = Goto(self.debug_closure, NT)


@utils.Debug.print(names=['debug_closure', 'debug_goto'])
def getLR0Analyser():
    g = elements.GrammarBuilder(filename='grammar3.txt').build()
    return LR0Analyser(g)


if __name__ == '__main__':
    getLR0Analyser()