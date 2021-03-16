from unittest import TestCase

import wdltest

class TestWdlTest(TestCase):
  def testHelloIsString(self):
    self.assertTrue(wdltest.hello() == "wdltest hello")

  #def testAnalysis(self):
    #exitCode = wdltest.server_testrun()
    #self.assertTrue(exitCode == 0)

  def testAnalysis(self):
    exitCode = wdltest.local_testrun()
    self.assertTrue(exitCode == 1)

if __name__ == "__main__":
    unittest.main()
