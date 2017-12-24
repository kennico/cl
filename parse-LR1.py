import LRParser
import debug
import sys
from LR1 import Parser


@debug.log_attr(msg='MAIN', log_obj=True)
def main():
    filename = sys.argv[1]
    g = LRParser.AugmentedGrammarBuilder(filename=filename).build()
    parser = Parser(g)

    with open(sys.argv[2]) as f:
        inputs = f.read().strip().splitlines()
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

    return 'Passed %d test.' % \
           passed

if __name__ == '__main__':
    main()