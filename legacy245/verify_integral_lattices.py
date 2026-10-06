"""Independent exact checks for two finite steps of the all-lattice IHS proof.

Uses only the Python standard library; no stored GAP output is read.
This checks the Hurwitz fixed stabilizer and the order-32 orbit arithmetic.
It does not verify the classification theorems or the geometric arguments.
"""
from fractions import Fraction
from itertools import combinations, product

I = ((0, -1, -1, -1), (1, 0, -1, 0), (0, 0, -1, -1), (0, 0, 2, 1))
J = ((0, 1, -1, 0), (0, 1, 0, 1), (1, 1, 0, 1), (0, -2, 0, -1))


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))


def negative(a):
    return tuple(tuple(-x for x in row) for row in a)


def apply(a, v):
    return tuple(sum(x * y for x, y in zip(row, v)) for row in a)


def rank(a):
    rows = [list(map(Fraction, row)) for row in a]
    result = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(result, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[result], rows[pivot] = rows[pivot], rows[result]
        value = rows[result][column]
        rows[result] = [x / value for x in rows[result]]
        for i in range(result + 1, len(rows)):
            value = rows[i][column]
            rows[i] = [x - value * y for x, y in zip(rows[i], rows[result])]
        result += 1
    return result


K = multiply(I, J)
quaternions = [identity(4), I, J, K, negative(identity(4)),
               negative(I), negative(J), negative(K)]
assert len(set(quaternions)) == 8
assert all(multiply(a, b) in quaternions for a in quaternions for b in quaternions)

# Coordinates represent twice a two-torsion point, so equality is modulo 2.
fixed = {v for v in product(range(2), repeat=4)
         if all(tuple((a - b) % 2 for a, b in zip(apply(q, v), v)) == (0,) * 4
                for q in quaternions)}
assert fixed == {(0, 0, 0, 0), (0, 1, 1, 0), (1, 0, 1, 0), (1, 1, 0, 0)}


def wreath(q, r, swap):
    zero = (0,) * 4
    return (tuple((zero + row if swap else row + zero) for row in q)
            + tuple((row + zero if swap else zero + row) for row in r))


group = [wreath(q, r, swap) for q in quaternions for r in quaternions
         for swap in (False, True)]
point = (0, 0, 0, 1, 0, 0, 1, 0)
stabilizer = []
for g in group:
    difference = tuple((a - b) % 2 for a, b in zip(apply(g, point), point))
    if difference[:4] == difference[4:] and difference[:4] in fixed:
        stabilizer.append(g)
reflections = [g for g in stabilizer
               if rank(tuple(tuple(int(i == j) - g[i][j] for j in range(8))
                             for i in range(8))) == 4]
generated, pending = {identity(8)}, [identity(8)]
while pending:
    a = pending.pop()
    for b in reflections:
        c = multiply(a, b)
        if c not in generated:
            generated.add(c)
            pending.append(c)
assert (len(group), len(stabilizer), len(reflections), len(generated)) == (128, 16, 2, 4)
print('Hurwitz: |Q8|=8; |B^Q8|=4; |wreath|=128; '
      '|full stabilizer|=16; reflections=2; |reflection subgroup|=4.')


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def quadratic(a):
    return sum(a[i] * a[j] for i in range(4) for j in range(i + 1, 4)) % 2


vectors = list(product(range(2), repeat=4))
singular = [v for v in vectors if any(v) and quadratic(v) == 0]
anisotropic = [v for v in vectors if quadratic(v) == 1]
assert len(singular) == 5 and len(anisotropic) == 10
assert len({add(a, b) for a, b in combinations(singular, 2)}) == 10
for v in singular:
    assert any(quadratic(a) == 1 and quadratic(add(a, v)) == 1 for a in vectors)

solutions = []
for t in (1, 2, 4, 8, 16):
    if (16 - t) % 4:
        continue
    possible = [m for m in range(33)
                if 64 - 3 * t + 8 * m in (1, 2, 4, 8, 16, 32, 64, 128, 256)]
    for multiplicities in product(possible, repeat=5):
        if 256 == 160 - 9 * t + 8 * sum(multiplicities):
            solutions.append((t, multiplicities))
assert {t for t, _ in solutions} == {16}
assert [(t, ms) for t, ms in solutions
        if all(64 - 3 * t + 8 * m >= 64 for m in ms)] == [(16, (6, 6, 6, 6, 6))]
print('Order 32: five singular directions and ten pair sums; '
      'orbit equations force t=16; component lower bound forces F_i=64.')
print('ALL_INDEPENDENT_IHK_FINITE_CHECKS_PASSED')
