import doctest
import pytest
import random

from glue import lal


def random_gps():
    return lal.LIGOTimeGPS(
        random.randint(-100000000, +100000000),
        random.randint(0, 999999999),
    )


def test_docstrings():
    doctest.testmod(lal, raise_on_error=True, verbose=True)


class TestLIGOTimeGPS:
    @pytest.mark.parametrize("args", [
        (100.5,),
        (100.500000000,),
        (100.50000000000000000000000,),
        (100, "500000000"),
        (100, "500000000.0000000000000"),
        (101, "-500000000"),
        (101, "-500000000.0000000000000"),
        ("100.5",),
        ("100.500000000",),
        ("100.50000000000000000000000",),
        ("100", 500000000),
        ("100", 500000000.0000000000000),
        ("101", -500000000),
        ("101", -500000000.0000000000000),
        ("100", "500000000"),
        ("100", "500000000.0000000000000"),
        ("101", "-500000000"),
        ("101", "-500000000.0000000000000"),
        (0, 100500000000),
        (0, 100500000000.0000000000000),
        (99, 1500000000),
        (99.5, 1000000000),
        (-10, 110500000000),
        (-10.5, 111000000000)
    ])
    def test__init__(self, args):
        assert lal.LIGOTimeGPS(*args) == lal.LIGOTimeGPS(100, 500000000)

    def test__float__(self):
        assert float(lal.LIGOTimeGPS(100.5)) == 100.5

    @pytest.mark.parametrize(("value"), [
        100.1,
        100.9,
    ])
    def test__int__(self, value):
        assert int(lal.LIGOTimeGPS(value)) == 100

    def testns(self):
        assert lal.LIGOTimeGPS(100.5).ns() == 100500000000

    @pytest.mark.parametrize(("value", "result"), [
        (100.5, True),
        (0, False),
    ])
    def test__nonzero__(self, value, result):
        assert bool(lal.LIGOTimeGPS(value)) is result

    @pytest.mark.parametrize(("a", "b", "result"), [
        (lal.LIGOTimeGPS(100.5), 10, lal.LIGOTimeGPS(110.5)),
        (lal.LIGOTimeGPS(100.5), lal.LIGOTimeGPS(10), lal.LIGOTimeGPS(110.5)),
    ])
    def test__add__(self, a, b, result):
        assert a + b == result

    @pytest.mark.parametrize(("a", "b", "result"), [
        (lal.LIGOTimeGPS(5), 2, lal.LIGOTimeGPS(10)),
        (lal.LIGOTimeGPS(20), 0.5, lal.LIGOTimeGPS(10)),
        (lal.LIGOTimeGPS(1000), 0, lal.LIGOTimeGPS(0)),
    ])
    def test__mul__(self, a, b, result):
        assert a * b == result

    @pytest.mark.parametrize(("a", "b", "result"), [
        (lal.LIGOTimeGPS(20), 2, lal.LIGOTimeGPS(10)),
        (lal.LIGOTimeGPS(5), .5, lal.LIGOTimeGPS(10)),
    ])
    def test__div__(self, a, b, result):
        assert a / b == result

    @pytest.mark.parametrize(("value", "mod", "result"), [
        (lal.LIGOTimeGPS(13), 5., lal.LIGOTimeGPS(3)),
    ])
    def test__mod__(self, value, mod, result):
        assert value % mod == result

    @pytest.mark.parametrize("operator", [
        "add",
        "sub",
        "mul",
        "div",
    ])
    def test_swig_comparison_1(self, operator):
        swiglal = pytest.importorskip("lal")

        def toswig(x):
            return swiglal.LIGOTimeGPS(str(x))

        def fromswig(x):
            return lal.LIGOTimeGPS(str(x))

        op = getattr(lal.LIGOTimeGPS, f"__{operator}__")
        swigop = getattr(swiglal.LIGOTimeGPS, f"__{operator}__")

        if operator in {"mul", "div", "mod"}:
            for i in range(1000):
                arg1 = random_gps() / 100
                arg2 = 100 ** (random.random() * 2 - 1)
                result = fromswig(swigop(toswig(arg1), arg2))
                expected = op(arg1, arg2)
                assert abs(result - expected) <= 1e-9  # approx
        else:
            for i in range(1000):
                arg1 = random_gps() / 2.
                arg2 = random_gps() / 2.
                assert fromswig(swigop(toswig(arg1), toswig(arg2))) == op(arg1, arg2)
