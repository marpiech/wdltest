from unittest import TestCase

import wdltest

class TestWdlTest(TestCase):
  def testHelloIsString(self):
    s = wdltest.hello()
    self.assertTrue(isinstance(s, basestring))

  def testReadConfig(self):
    self.assertTrue(False, str(wdltest.config().sections()))
    #self.assertTrue(wdltest.config())

if __name__ == "__main__":
    unittest.main()
