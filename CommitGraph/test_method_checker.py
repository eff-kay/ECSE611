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

    def test_with_exception(self):
        assert self.mc('if (!fs.exists(parentdir))')

    def test_signature(self):
        assert self.mc('return MAPPER.writeValueAsString(object)')\
            .method_signature == 'MAPPER.writeValueAsString(object)'

    def test_not_for_loop(self):
        assert not self.mc('for(int i = 0; i < vectorSize; i++) {')

    def test_is_not_class(self):
        assert not self.mc('SuppressWarnings("unused")')
