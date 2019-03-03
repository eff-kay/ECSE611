import unittest

from CommitGraph.method_checker import MethodChecker

class TestFunctionChecker(unittest.TestCase):
    def setUp(self):
        self.mc = MethodChecker

    def test_with_new_object_creation(self):
        assert not self.mc('new ObjectMapper()')
