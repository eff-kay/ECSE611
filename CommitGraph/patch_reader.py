import os
import subprocess
import re

HIVE_GIT_COMMAND = "git clone https://git-wip-us.apache.org/repos/asf/hive.git"
HBASE_GIT_COMMAND = "git clone https://gitbox.apache.org/repos/asf/hbase.git"

class GetPatch:
    """
    We give this two commits (the commit in question and the prevous commit).
    This will give us access to the patch

    Running #get_patch will get you the patch as a string.
    """
    REPO_TO_COMMAND = {
        'hbase': HBASE_GIT_COMMAND,
        'hive': HIVE_GIT_COMMAND,
    }

    SAVE_CURRENT_WORKING_DIRECTORY = 'CURR_DIR=$PWD'
    GO_BACK_TO_WORKING_DIRECTORY = 'cd $CURR_DIR'

    def __init__(self, repo_name):
        self.repo_name = repo_name

        if repo_name not in ['hbase', 'hive']:
            raise NotImplementedError(f'{self.repo_name} must be either "hive" or "hbase"')

        if not os.path.exists(f'./Repo/{self.repo_name}'):
            subprocess.call(self.REPO_TO_COMMAND[self.repo_name])

        print(f'{self.repo_name} exists in ./Repo/{self.repo_name}...')

    def get_patch(self, commit_hash, previous_commit_hash):
        return subprocess.check_output(";".join([
            self.SAVE_CURRENT_WORKING_DIRECTORY,
            self.go_to_target_directory(),
            self.diff_command(commit_hash, previous_commit_hash),
            self.GO_BACK_TO_WORKING_DIRECTORY,
        ]), shell=True).decode('utf-8')

    def go_to_target_directory(self):
        return f'cd Repo/{self.repo_name}'

    def diff_command(self, commit_hash, previous_commit_hash):
        return f'git diff {commit_hash} {previous_commit_hash}'

class PatchSection:
    """
    At this point, each diff section has the following format:

    BOF >>

    a/... b/... (modified filenames)
    index [shortened hash] [???]
    --- a/...
    --- b/...

    @@ -[starting line], [lines before] +[starting line],[lines after] @@
    ...

    @@ ... @@

    << EOF

    We split this into
    1. the header (which contains which file was modified)
    2. the lines modified (the part between the @@s)
    3. the actual change

    (2) and (3) have to occur in pairs
    """

    def __init__(self, repo_name, section):
        self.repo_name = repo_name
        self.section = section

        self.header, *lines_modified_with_changes = section.split('@@')

        self.filename = re.search(r'a/.* ', self.header).group().rstrip(' ').lstrip('a/')

        self._lines_modified_with_changes = self._split_into_pairs(lines_modified_with_changes)
        self.chunks = [Change(
            changeline=lm[0],
            changes=lm[1],
            filename=self.filename,
            ) for lm in self._lines_modified_with_changes]

    def _split_into_pairs(self, l):
        return [l[i:i+2] for i in range(0, len(l), 2)]

class Change:
    def __init__(self, changeline, changes, filename):
        self.changeline = changeline
        self.changes = [change for change in changes.split('\n') if change]
        self.filename = filename

    @property
    def method_changed(self):
        raise NotImplementedError

class PatchSplitter:
    SECTION_SPLITS = 'diff --git'
    # CHUNK_SEARCH = re.compile('@@.*@@')

    def __init__(self, repo_name, patch_section=PatchSection):
        self.repo_name = repo_name
        self.patch_section = PatchSection

    def split_by_diff_section(self, patch):
        # this will remove self.SECTION_SPLITS, filter out empties
        diff_sections = [section for section in patch.split(self.SECTION_SPLITS) if section]

        disassembled_patch = []

        for diff_section in diff_sections:
            patch_section = self.patch_section(self.repo_name, diff_section)
            disassembled_patch.append(patch_section)

        return disassembled_patch

# notes on usage
# gp = GetPatch('hbase')
# patch = gp.get_patch('f0032c925510877396b1b0979abcc2ce83e67529', '482b505796e1dfe33551c1d20af2ff9d1d6a38dc')
# ps = PatchSplitter('hbase')
# patches = ps.split_by_diff_section(patch)
