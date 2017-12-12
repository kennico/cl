from itertools import chain
from collections import defaultdict

import utils


class Symbol(object):
    def __init__(self, s):
        self.string = s

    def __str__(self):
        return self.string

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.string)

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.string == other.string
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Terminal(Symbol):
    pass


class Production(object):
    def __init__(self, head, *body):
        self.head = head
        self.body = body

    def __str__(self):
        return '%s->%s' % (str(self.head), ''.join([str(s) for s in self]))

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.__str__())

    def __getitem__(self, index):
        """Return the i-th symbol of the production body"""

        return self.body[index]

    def __len__(self):
        return self.body.__len__()

    def __eq__(self, other):
        if isinstance(other, Production):
            return (self.head == other.head) and (self.body == other.body)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class NTerminal(Symbol):
    def __init__(self, s):
        super(NTerminal, self).__init__(s)
        self.productions = []
        self.derive_epsilon = None

    def create_production(self, *body):
        p = Production(self, *body)
        self.productions.append(p)
        return p


class Grammar(object):
    def __init__(self):
        self.NT = None
        self.T = None
        self.START = None
        self.EPSILON = None

    def nterminals(self):
        return self.NT.values()

    def terminals(self):
        return self.T.values()

    def productions(self):
        # TODO Add list()
        return list(chain(*[sym.productions for sym in self.NT.values()]))


class GrammarBuilder(object):
    def __init__(self, *prods, **kwargs):
        self.raw_start = kwargs.pop('start', 'S')
        self.raw_epsilon = kwargs.pop('epsilon', 'e')

        if not prods:
            try:
                filename = kwargs.pop('filename')
            except KeyError:
                raise ValueError('No productions or filename found.')
            with open(filename) as f:
                self.raw_lines = [line.strip() for line in f]
        else:
            self.raw_lines = [line.strip() for line in prods]

    def pre_process(self):
        raw_productions = defaultdict(list)
        for l in self.raw_lines:
            nts, *prods = l.split()
            raw_productions[nts] += prods
        self.raw_productions = raw_productions

    def is_NT(self, s):
        return s in self.raw_productions

    def symbol(self, s):
        if s not in self.tempd:
            if self.is_NT(s):
                nt = self.tempd[s] = NTerminal(s)
                for raw_prod in self.raw_productions[s]:
                    if raw_prod == self.raw_epsilon:
                        nt.derive_epsilon = True
                        body = []
                    else:
                        body = [self.symbol(c) for c in raw_prod]
                    nt.create_production(*body)
            else:
                self.tempd[s] = Terminal(s)
        return self.tempd[s]

    @utils.Debug.print(names=['START'], meths=['nterminals', 'terminals', 'productions'])
    def build(self):
        self.tempd = {}
        self.pre_process()
        self.symbol(self.raw_start)

        g = Grammar()
        g.START = self.tempd[self.raw_start]
        g.NT = {s:obj for s, obj in self.tempd.items() if self.is_NT(s)}
        g.T = {s:obj for s, obj in self.tempd.items() if not self.is_NT(s)}

        return g


def main():
    g = GrammarBuilder(filename='grammar2.txt', start='S', epsilon='e').build()



if __name__ == '__main__':
    main()
