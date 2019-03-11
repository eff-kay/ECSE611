import unittest

from CommitGraph.function_checker import FunctionChecker

class TestFunctionChecker(unittest.TestCase):
    def setUp(self):
        self.fc = FunctionChecker

    def test_with_plain_method(self):
        assert self.fc('write(Object object)').is_function

    def test_module_level_method_call(self):
        assert not self.fc('HbaseClassTestRule.forClass()')

    def test_with_method_call(self):
        assert not self.fc('write()').is_function

    def test_with_method_call_and_arguments(self):
        assert not self.fc('ReentrantLock(true)')

    def test_with_multiple_arguments(self):
        assert not self.fc('GSON.fromJson(json, typeOfHashMap)')

    def test_with_modifiers(self):
        assert self.fc('public static String toJSON(String filename, NavigableSet<CachedBlock> blocks)')

    def test_log_statement(self):
        assert not self.fc('LOG.trace("Getting attribute " + prs + " of " + oname + " threw " + e);')

    def test_with_partial_method(self):
        assert self.fc('private static void writeAttribute(JsonWriter writer, String attName, String descriptionStr,')

    def test_no_parameters(self):
        assert not self.fc('public void testSearchJson() throws JsonProcessingException, IOException {')

    def test_with_map(self):
        assert self.fc('public static String writeMapAsString(Map<String, Object> map) throws IOException')

    def test_with_single_parameter(self):
        assert self.fc('public static String writeObjectAsString(Object object) throws IOException')

    def test_with_prototype(self):
        assert not self.fc('void write(String key, String value) throws IOException;')

    def test_with_protected(self):
        assert self.fc('protected String[] splitColonSeparated(String option,')

    def test_with_private(self):
        assert self.fc('private void parseColumnFamilyOptions(CommandLine cmd) {')
