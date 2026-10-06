"""Exact shared operations; stored witnesses are checked, never trusted flags."""
from sage.all import QQ, matrix, identity_matrix, PolynomialRing
from collections import Counter


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def closure(generators, expected=None):
    one = identity_matrix(QQ, 4)
    one.set_immutable()
    found = {one}
    todo = [one]
    for g in todo:
        for h in generators:
            k = g*h
            k.set_immutable()
            if k not in found:
                found.add(k)
                todo.append(k)
        require(len(found) <= 1152, 'Unexpected group size')
    if expected is not None:
        require(len(found) == expected, 'Wrong full group order')
    return found


def molien(group):
    R = PolynomialRing(QQ, 't')
    K = R.fraction_field()
    counts = Counter(tuple(g.charpoly().list()) for g in group)
    return sum(QQ(n)/len(group)/K(R(list(reversed(coefficients))))
               for coefficients, n in counts.items())


def strings(M):
    return [[str(c) for c in row] for row in M.rows()]


def frozen(M):
    M.set_immutable()
    return M
