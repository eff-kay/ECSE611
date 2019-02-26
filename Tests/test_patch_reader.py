import unittest

from CommitGraph.patch_reader import GetPatch
from CommitGraph.patch_reader import PatchSplitter
from CommitGraph.patch_reader import PatchSection

example_section = """diff --git a/hbase-client/pom.xml b/hbase-client/pom.xml
index bb99eec..96367df 100644 (file)
--- a/hbase-client/pom.xml
+++ b/hbase-client/pom.xml
@@ -182,7 +182,6 @@
    <dependency>
      <groupId>org.apache.commons</groupId>
      <artifactId>commons-crypto</artifactId>
-     <version>${commons-crypto.version}</version>
      <exclusions>
        <exclusion>
          <groupId>net.java.dev.jna</groupId>
@@ -190,10 +189,6 @@
        </exclusion>
      </exclusions>
    </dependency>
-   <dependency>
-     <groupId>com.fasterxml.jackson.core</groupId>
-     <artifactId>jackson-databind</artifactId>
-   </dependency>
  </dependencies>

<profiles>
"""

class TestGetPatch(unittest.TestCase):
    def setUp(self):
        self.gp = GetPatch
        self.target_repo = 'hbase'

        self.commit = 'f0032c925510877396b1b0979abcc2ce83e67529'
        self.previous_commit = '482b505796e1dfe33551c1d20af2ff9d1d6a38dc'

    def test_init(self):
        assert self.gp(self.target_repo)

    def test_get_patch(self):
        patch = self.gp(self.target_repo).get_patch(self.commit, self.previous_commit)

        assert isinstance(patch, str)

class TestPatchSplitter(unittest.TestCase):
    def setUp(self):
        self.ps = PatchSplitter('hbase')

    def test_split_by_diff_section(self):
        disassembled_patch = self.ps.split_by_diff_section(example_section)

        assert len(disassembled_patch) == 1

class TestPatchSection(unittest.TestCase):
    def setUp(self):
        self.ps = PatchSection('hbase', example_section.lstrip('diff --git'))

    def test_header(self):
        header = \
        "a/hbase-client/pom.xml b/hbase-client/pom.xml\n"\
        "index bb99eec..96367df 100644 (file)\n"\
        "--- a/hbase-client/pom.xml\n"\
        "+++ b/hbase-client/pom.xml\n"\

        assert self.ps.header == header
