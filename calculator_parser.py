import re


class _Token:
    def __init__(self, kind, value=None):
        self.kind = kind
        self.value = value


class _TokenStream:
    pattern = re.compile(
        r"\s*((?P<op>[-+*/()^])|"
        r"(?P<num>((\d*\.\d+)|(\d+\.?))([eE][-+]?\d+)?(?![eE\d\.]))|"
        r"(?P<ans>ans))\s*"
    )

    def __init__(self, string):
        self.__i = 0
        self.__len = len(string)
        self.__string = string
        self.__putback = False

    def getToken(self):
        if self.__putback:
            self.__putback = False
            return self.__buffer

        if self.__i == self.__len:
            return _Token("eos")

        if match := _TokenStream.pattern.match(self.__string, self.__i):
            self.__i = match.end()
            if kind := match.group("op"):
                return _Token(kind)
            elif val := match.group("num"):
                return _Token("n", float(val))
            elif match.group("ans"):
                return _Token("n", calc.ans)
        else:
            raise SyntaxError("invalid syntax")

    def putback(self, token):
        if self.__putback:
            raise SystemError("full buffer")
        else:
            self.__buffer = token
            self.__putback = True


# Grammar
# Expression:
#     Term
#     Expression '+' Term
#     Expression '-' Term
# Term:
#     Primary
#     Term '*' Primary
#     Term '/' Primary
# Primary:
#     Number
#     '(' Expression ')'
#     Primary '(' Expression ')'
#     [-+ ]* Primary
#     Primary '^' Primary
# Number:
#     floating-point-literal


def calc(exp):
    ts = _TokenStream(exp)

    def expression(primaryCall=False):
        val = term()

        while True:
            token = ts.getToken()

            if token.kind == "+":
                val += term()
            elif token.kind == "-":
                val -= term()
            elif primaryCall and token.kind == ")":
                return val
            elif token.kind == "eos":
                ts.putback(token)
                return val
            else:
                raise SyntaxError("invalid syntax")

    def term():
        val = primary()

        while True:
            token = ts.getToken()

            if token.kind == "*":
                val *= primary()
            elif token.kind == "/":
                val /= primary()
            else:
                ts.putback(token)
                return val

    def primary():
        token = ts.getToken()
        val = 0.0
        positive = True
        count = 0

        # Find the sign
        while True:
            if token.kind not in ("+", "-"):
                positive = True if count % 2 == 0 else False
                break
            if token.kind == "-":
                count += 1
            token = ts.getToken()

        # Find the value
        if token.kind == "n":
            val = token.value
        elif token.kind == "(":
            val = expression(True)
        else:
            raise SyntaxError("invalid syntax")

        while True:
            token = ts.getToken()

            if token.kind == "(":
                n = expression(True)

                token = ts.getToken()
                if token.kind == "^":
                    n **= primary()
                else:
                    ts.putback(token)

                val *= n
            elif token.kind == "^":
                val **= primary()
            else:
                ts.putback(token)
                return val if positive else -val

    calc.ans = expression()
    return calc.ans


calc.ans = 0.0

if __name__ == "__main__":

    def _printError(e, errType=None):
        err = type(e).__name__ if errType is None else errType
        if msg := str(e):
            err += ": " + msg
        print(err)

    while True:
        inp = input(">> ")

        if inp == "end":
            break
        else:
            try:
                print("= " + str(calc(inp)))
            except ArithmeticError as e:
                _printError(e, "MathError")
            except Exception as e:
                _printError(e)
