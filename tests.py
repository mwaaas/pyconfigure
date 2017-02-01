""" Tests for configure"""

from unittest import TestCase as BaseTestCase, skip
from configure import Configuration, Ref, Factory
from os import path
from datetime import timedelta

TEST_CONCAT_STRING = "base_test"

class A(object):

    def __init__(self, a, b=3):
        self.a = a
        self.b = b


def a(a, b=4):
    return A(a, b=b)


def kw(**kw):
    return kw


class TestCase(BaseTestCase):

    def config(self, v, ctx=None, configure=True):
        return Configuration.from_string(v.strip(), ctx=ctx,
                                         configure=configure)

    @skip("removed interpolation")
    def test_interpolation(self):
        c = self.config("""
a: "%(a)s"
b: "%(b)s"
        """, {"a": "aa", "b": "bb"})
        self.assertEqual(c.a, "aa")
        self.assertEqual(c.b, "bb")

    def test_ref(self):
        c = self.config("""
a: 1
b:
    c: !ref:a
    d: !ref:..a
e: !ref:.b
        """)
        self.assertEqual(c.a, 1)
        # self.assertEqual(c.e(c), c.b)
        # self.assertEqual(c.b.c(c.b), c.a)
        # self.assertEqual(c.b.d(c.b), c.a)

    def test_factory(self):
        c = self.config("""
a1:
    a: 1
a2:
    a: 2
    b: 4
a3:
    a: 3
a4:
    a: 4
    b: 5
        """)
        o = Factory(A, c.a1)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 1)
        self.assertEqual(o.b, 3)

        o = Factory(A, c.a2)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 2)
        self.assertEqual(o.b, 4)

        o = Factory(a, c.a3)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 3)
        self.assertEqual(o.b, 4)

        o = Factory(a, c.a4)(c)
        self.assertTrue(isinstance(o, A))
        self.assertEqual(o.a, 4)
        self.assertEqual(o.b, 5)

    def test_factory_kw(self):
        c = self.config("""
a: !factory:tests.kw
    a: 4
    b: 5
        """)
        c.configure()
        self.assertTrue('a' in c.a)
        self.assertTrue('b' in c.a)

    def test_graph(self):
        c = self.config("""
a: !factory:tests.A
    a: 1
    b: !ref:.b
b: !factory:tests.a
    a: 3
        """)
        c.configure()
        self.assertTrue(isinstance(c.a, A))
        self.assertEqual(c.a.a, 1)
        self.assertTrue(isinstance(c.b, A))
        self.assertEqual(c.b.a, 3)
        self.assertTrue(isinstance(c.a.b, A))
        self.assertEqual(c.a.b.a, c.b.a)
        self.assertEqual(c.a.b.b, c.b.b)
        self.assertTrue(c.a.b is c.b)

    def test_obj(self):
        c = self.config("""
a: !obj:tests.A
b: !obj:tests.a
        """)
        c.configure()
        self.assertTrue(c.a is A)
        self.assertTrue(c.b is a)

    def test_concat(self):
        c = self.config("""
a: !concat tests.TEST_CONCAT_STRING "/test1"
b: !concat tests.TEST_CONCAT_STRING '/test2' "/test3/" tests.TEST_CONCAT_STRING
        """)
        c.configure()
        self.assertEqual(c.a, "base_test/test1")
        self.assertEqual(c.b, "base_test/test2/test3/base_test")

    def test_concat_implicit_resolver(self):
        c = self.config("""
a: tests.TEST_CONCAT_STRING "/test1"
b: tests.TEST_CONCAT_STRING '/test2' "/test3/" tests.TEST_CONCAT_STRING
        """)
        c.configure()
        self.assertEqual(c.a, "base_test/test1")
        self.assertEqual(c.b, "base_test/test2/test3/base_test")

    def test_load_from_file(self):
        filename = path.join(path.dirname(__file__), 'examples', 'example.default.conf')
        c = Configuration.from_file(filename)
        c.configure()

        self.assertEqual(c.a, 1)
        self.assertIsInstance(c.b, timedelta)
        self.assertEqual(c.b, timedelta(days=1))

    def test_load_from_file_inheritance(self):
        filename = path.join(path.dirname(__file__), 'examples', 'example.conf')
        c = Configuration.from_file(filename)
        c.configure()

        self.assertEqual(c.a, 100)
        self.assertIsInstance(c.b, timedelta)
        self.assertEqual(c.b, timedelta(days=1))
        self.assertEqual(c.c, "value")

    def test_inheritance_of_yaml_section(self):
        c = self.config(
            """
person_a:
    name: Francis Mwangi
    age: 23
person_b:
    inherit: person_a
    age: 30
            """
        )

        self.assertEqual(c.person_a.name, "Francis Mwangi")
        self.assertEqual(c.person_a.age, 23)

        self.assertEqual(c.person_b.name, "Francis Mwangi")
        self.assertEqual(c.person_b.age, 30)

        self.assertTrue(len(c.person_b)==2)


    def test_converting_to_dict(self):
        c = self.config(
            """
person_a:
    name: Francis Mwangi
    age: 23
person_b:
    inherit: person_a
    age: 30
    relatives:
        dad: Michael Muraya
        mother: Rachael Njeri
        inlaw:
            dad: Tom
            mother: auma
            """,
            configure=False
        )

        expected_dict = dict(
                person_a=dict(
                    name="Francis Mwangi",
                    age=23
                ),
                person_b=dict(
                    name="Francis Mwangi",
                    age=30,
                    relatives=dict(
                        dad="Michael Muraya",
                        mother="Rachael Njeri",
                        inlaw=dict(
                            dad="Tom",
                            mother="auma"
                        )
                    )
                )
            )

        self.assertEqual(
            expected_dict,
            c
        )

