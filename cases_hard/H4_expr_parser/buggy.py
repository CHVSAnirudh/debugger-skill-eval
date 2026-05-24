"""Recursive-descent arithmetic expression evaluator.

Grammar (standard, left-associative):
    expr   = term (('+' | '-') term)*
    term   = factor (('*' | '/') factor)*
    factor = NUMBER | '(' expr ')' | '-' factor

Used by the spreadsheet engine to evaluate cell formulas like
`= 20 / 2 / 5` or `= (3 + 4) * 2`.
"""

from __future__ import annotations

import json
import sys


class ParseError(Exception):
    pass


def tokenize(source: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(source):
        c = source[i]
        if c.isspace():
            i += 1
            continue
        if c in "+-*/()":
            tokens.append(c)
            i += 1
            continue
        if c.isdigit() or c == ".":
            j = i
            while j < len(source) and (source[j].isdigit() or source[j] == "."):
                j += 1
            tokens.append(source[i:j])
            i = j
            continue
        raise ParseError(f"unexpected character {c!r} at position {i}")
    return tokens


class Parser:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _advance(self) -> str:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def parse(self) -> float:
        value = self.expr()
        if self.pos != len(self.tokens):
            raise ParseError(f"trailing tokens at position {self.pos}")
        return value

    def expr(self) -> float:
        value = self.term()
        while self._peek() in ("+", "-"):
            op = self._advance()
            right = self.term()
            if op == "+":
                value = value + right
            else:
                value = value - right
        return value

    def term(self) -> float:
        value = self.factor()
        if self._peek() in ("*", "/"):
            op = self._advance()
            right = self.term()
            if op == "*":
                value = value * right
            else:
                value = value / right
        return value

    def factor(self) -> float:
        tok = self._peek()
        if tok is None:
            raise ParseError("unexpected end of input")
        if tok == "-":
            self._advance()
            return -self.factor()
        if tok == "(":
            self._advance()
            value = self.expr()
            if self._peek() != ")":
                raise ParseError("missing closing paren")
            self._advance()
            return value
        if tok.replace(".", "", 1).isdigit():
            self._advance()
            return float(tok)
        raise ParseError(f"unexpected token {tok!r}")


def evaluate(expression: str) -> float:
    tokens = tokenize(expression)
    return Parser(tokens).parse()


def _format(value: float) -> str:
    # Show integers without trailing .0 for cleaner golden comparison.
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


if __name__ == "__main__":
    data = json.load(sys.stdin)
    results = []
    for expr in data["expressions"]:
        try:
            v = evaluate(expr)
            results.append(f"{expr} = {_format(v)}")
        except ParseError as e:
            results.append(f"{expr} = ERROR: {e}")
    print("\n".join(results))
