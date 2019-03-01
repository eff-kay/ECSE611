import unittest

from CommitGraph.class_checker import ClassChecker

class TestClassChecker(unittest.TestCase):
    def setUp(self):
        self.cc = ClassChecker

    def test_with_plain_class(self):
        assert self.cc('class Raster;').is_class

    def test_with_extension(self):
        assert self.cc('public class JMXJsonServlet extends HttpServlet').is_class

    def test_class_signature(self):
        cc = self.cc('public class JMXJsonServlet extends HttpServlet')
        assert cc.class_signature == 'public class JMXJsonServlet'

    def test_method_call_with_signature_inside(self):
        cc = self.cc('.registerTypeAdapter(LongAddr.class, new TypeAdapter<LongAdder>() {')
        assert not cc
