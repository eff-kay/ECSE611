import unittest

from CommitGraph.method_checker import MethodChecker

class TestFunctionChecker(unittest.TestCase):
    def setUp(self):
        self.mc = MethodChecker

    def test_with_new_object_creation(self):
        assert not self.mc('new ObjectMapper()')

    def test_with_private_keyword(self):
        assert not self.mc('private JsonMapper()')

    def test_with_module_name(self):
        assert self.mc('return MAPPER.writeValueAsString(object)')

    def test_signature(self):
        assert self.mc('return MAPPER.writeValueAsString(object)')\
            .method_signature == 'MAPPER.writeValueAsString(object)'
