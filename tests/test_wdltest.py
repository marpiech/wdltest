from unittest import TestCase

import wdltest

class TestWdlTest(TestCase):
  def testHelloIsString(self):
    self.assertTrue(wdltest.hello() == "wdltest hello")

  def testAnalysis(self):
    exitCode = wdltest.testrun()
    self.assertTrue(exitCode == 0)

if __name__ == "__main__":
    unittest.main()
