from antlr4 import *
from example_grammar import GrammarLexer, GrammarParser


input = "1 + 1"


def main():
    input_stream = InputStream(input)

    lexer = GrammarLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    parser = GrammarParser(token_stream)

    parser.addErrorListener(DiagnosticErrorListener())

    tree = parser.s() # start rule
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main()
