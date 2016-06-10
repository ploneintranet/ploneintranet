import time
import unittest2 as unittest
from BTrees.LLBTree import LLTreeSet

from ploneintranet.microblog.utils import longkeysortreverse


class TestLongkeysortreverse1(unittest.TestCase):

    def setUp(self):
        self.treeset = LLTreeSet()
        self.k0 = long(1)
        self.treeset.insert(self.k0)
        self.k1 = long((time.time() - 3600 * 25) * 1e6)
        self.treeset.insert(self.k1)
        self.k2 = long((time.time() - 3600 * 4) * 1e6)
        self.treeset.insert(self.k2)
        self.k3 = long((time.time() - 3600 * 3) * 1e6)
        self.treeset.insert(self.k3)
        self.k10 = long(time.time() * 1e6 - 10)
        self.treeset.insert(self.k10)
        self.k11 = self.k10 + 1
        self.treeset.insert(self.k11)

    def test_all(self):
        values = list(longkeysortreverse(self.treeset))
        expect = [self.k11, self.k10, self.k3, self.k2, self.k1, self.k0]
        self.assertEquals(values, expect)

    def test_min_hour(self):
        minv = long((time.time() - 3600) * 1e6)
        values = list(longkeysortreverse(self.treeset, minv=minv))
        expect = [self.k11, self.k10]
        self.assertEquals(values, expect)

    def test_max_hour(self):
        maxv = long((time.time() - 3600) * 1e6)
        values = list(longkeysortreverse(self.treeset, maxv=maxv))
        expect = [self.k3, self.k2, self.k1, self.k0]
        self.assertEquals(values, expect)

    def test_min_day(self):
        minv = long((time.time() - 3600 * 24) * 1e6)
        values = list(longkeysortreverse(self.treeset, minv=minv))
        expect = [self.k11, self.k10, self.k3, self.k2]
        self.assertEquals(values, expect)

    def test_max_day(self):
        maxv = long((time.time() - 3600 * 24) * 1e6)
        values = list(longkeysortreverse(self.treeset, maxv=maxv))
        expect = [self.k1, self.k0]
        self.assertEquals(values, expect)

    def test_min_day_max_hour(self):
        maxv = long((time.time() - 3600) * 1e6)
        minv = long((time.time() - 3600 * 24) * 1e6)
        values = list(longkeysortreverse(self.treeset,
                                         minv=minv,
                                         maxv=maxv))
        expect = [self.k3, self.k2]
        self.assertEquals(values, expect)

    def test_all_limit(self):
        values = list(longkeysortreverse(self.treeset, limit=3))
        expect = [self.k11, self.k10, self.k3]
        self.assertEquals(values, expect)

    def test_min_day_max_hour_limit(self):
        maxv = long((time.time() - 3600) * 1e6)
        minv = long((time.time() - 3600 * 24) * 1e6)
        values = list(longkeysortreverse(self.treeset,
                                         minv=minv,
                                         maxv=maxv,
                                         limit=1))
        expect = [self.k3]
        self.assertEquals(values, expect)


class TestLongkeysortreverse2(unittest.TestCase):
    """Replay real-life problem"""

    def setUp(self):
        self.treeset = LLTreeSet()
        for id in replay_ids:
            self.treeset.insert(id)

    def test_replay_ids(self):
        self.assertEquals(replay_ids, sorted(replay_ids))

    def test_all2(self):
        got = sorted(longkeysortreverse(self.treeset, None, None, None))
        expect = replay_ids
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)

    def test_minv(self):
        minv = 1465289825265391
        got = sorted(longkeysortreverse(self.treeset, minv, None, None))
        expect = [x for x in replay_ids if minv <= x]
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)

    def test_maxv(self):
        maxv = 1465894624580543
        got = sorted(longkeysortreverse(self.treeset, None, maxv, None))
        expect = [x for x in replay_ids if x <= maxv]
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)

    def test_limit_20(self):
        got = sorted(longkeysortreverse(self.treeset, None, None, 20))
        expect = replay_ids[-20:]
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)

    def test_limit_50(self):
        got = sorted(longkeysortreverse(self.treeset, None, None, 50))
        expect = replay_ids[-50:]
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)

    def test_minv_maxv(self):
        minv = 1465289825265391
        maxv = 1465894624580543
        got = sorted(longkeysortreverse(self.treeset, minv, maxv, None))
        expect = [x for x in replay_ids if minv <= x <= maxv]
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)

    def test_minv_limit(self):
        minv = 1465289825265391
        got = sorted(longkeysortreverse(self.treeset, minv, None, 20))
        expect = [x for x in replay_ids if minv <= x][-20:]
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)

    def test_maxv_limit(self):
        maxv = 1465894624580543
        got = sorted(longkeysortreverse(self.treeset, None, maxv, 20))
        expect = [x for x in replay_ids if x <= maxv][-20:]
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)

    def test_minv_maxv_limit(self):
        minv = 1465289825265391
        maxv = 1465894624580543
        got = sorted(longkeysortreverse(self.treeset, minv, maxv, 10))
        expect = [x for x in replay_ids if minv <= x <= maxv][-10:]
        self.assertEquals(len(got), len(expect))
        self.assertEquals(got, expect)


# this is a real set, but contains (at time of test coding) future updates!!!
replay_ids = [
    1465289821764142, 1465289821814609, 1465289822248430, 1465289822807139,
    1465289823102934, 1465289823177254, 1465289823237715, 1465289823445777,
    1465289823477344, 1465289823548460, 1465289823652171, 1465289824396396,
    1465289824433315, 1465289824506349, 1465289824543457, 1465289824766934,
    1465289825064447, 1465289825137837, 1465289825265391, 1465289825445317,
    1465290121916429, 1465290122065141, 1465290122413969, 1465290122451310,
    1465290122558669, 1465290122659182, 1465290122843146, 1465290123140248,
    1465290123381254, 1465290123413033, 1465290123713267, 1465290123804120,
    1465290123934625, 1465290124136372, 1465290124211522, 1465290124248667,
    1465290124877481, 1465290124952499, 1465290125356127, 1465290125533401,
    1465290125685000, 1465376221879331, 1465376221990943, 1465376222212724,
    1465376222302911, 1465376222357369, 1465376222590294, 1465376222733426,
    1465376222955957, 1465376223065925, 1465376223284023, 1465376223524688,
    1465376223572205, 1465376223595902, 1465376224024475, 1465376224617697,
    1465376224655610, 1465376224692645, 1465376224840411, 1465376225101525,
    1465419421693259, 1465419421716725, 1465419421740414, 1465419421790839,
    1465419422027607, 1465419422138401, 1465419422231017, 1465419422285479,
    1465419422696373, 1465419422880555, 1465419423619623, 1465419423891216,
    1465419424061152, 1465419424173841, 1465419424285857, 1465419424803044,
    1465419425220518, 1465419425488860, 1465419425610591, 1465894621622105,
    1465894621670697, 1465894622102347, 1465894622266980, 1465894622320320,
    1465894622487497, 1465894622525003, 1465894622621934, 1465894622769784,
    1465894622917980, 1465894623213156, 1465894623261422, 1465894623501969,
    1465894623682228, 1465894624321877, 1465894624580543, 1465894624914673,
    1465894625401119, 1467968221838136, 1467968221953515, 1467968222175534,
    1467968222338858, 1467968222375855, 1467968222991904, 1467968223028968,
    1467968223316572, 1467968223348387, 1467968223759332, 1467968223847828,
    1467968223979796, 1467968224098918, 1467968224359132, 1467968224469261,
    1467968224729651, 1467968224990235, 1467968225027332, 1467968225175325,
    1467968225310759, 1467968225573445, 1467968225647622]
