from unittest import TestCase

import wdltest

class TestHello(TestCase):
    def test_is_string(self):
        s = wdltest.hello()
        self.assertTrue(isinstance(s, basestring))
