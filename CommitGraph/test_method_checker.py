import unittest

from CommitGraph.method_checker import MethodChecker

class TestMethodChecker(unittest.TestCase):
    def setUp(self):
        self.mc = MethodChecker

    def test_with_plain_method(self):
        assert self.mc('write(Object object)').is_method

    def test_module_level_method_call(self):
        assert not self.mc('HbaseClassTestRule.forClass()')

    def test_with_method_call(self):
        assert not self.mc('write()').is_method

    def test_with_method_call_and_arguments(self):
        assert not self.mc('ReentrantLock(true)')

    def test_with_multiple_arguments(self):
        assert not self.mc('GSON.fromJson(json, typeOfHashMap)')

    def test_with_modifiers(self):
        assert self.mc('public static String toJSON(String filename, NavigableSet<CachedBlock> blocks)')

    def test_log_statement(self):
        assert not self.mc('LOG.trace("Getting attribute " + prs + " of " + oname + " threw " + e);')

    def test_with_partial_method(self):
        assert self.mc('private static void writeAttribute(JsonWriter writer, String attName, String descriptionStr,')

    def test_no_parameters(self):
        assert not self.mc('public void testSearchJson() throws JsonProcessingException, IOException {')
