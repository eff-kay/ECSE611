import os
import subprocess
import re
import itertools
import operator
import copy

# I really don't have time to fix this
try:
    from method_checker import MethodChecker
    from repo_executor import RepoExecutor
    from change import Change
except ModuleNotFoundError:
    from .method_checker import MethodChecker
    from .repo_executor import RepoExecutor
    from .change import Change


def get_patch(repo_name, commit_hash, parent_commit_hash):
    return RepoExecutor(repo_name).execute(
        f'git diff {commit_hash} {parent_commit_hash}'
    )

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

    def __init__(self, repo_name, section, commit, parent_commit):
        self.repo_name = repo_name
        self.section = section
        self.commit = commit
        self.parent_commit = parent_commit

        self.header, *lines_modified_with_changes = section.split('@@')

        self.filename = re.search(r'a/.* ', self.header).group().rstrip(' ').lstrip('a/')

        self._lines_modified_with_changes = self._split_into_pairs(lines_modified_with_changes)

        self.chunks = [Change(
            changeline=lm[0],
            changes=lm[1],
            filename=self.filename,
            commit=self.commit,
            parent_commit=self.parent_commit,
            repo_name=self.repo_name,
            ) for lm in self._lines_modified_with_changes]

    @property
    def modified_methods(self):
        methods = [chunk.changed_methods_and_classes() for chunk in self.chunks]
        return [methods_ for methods_ in methods if any(methods_)]

    def _split_into_pairs(self, l):
        return [l[i:i+2] for i in range(0, len(l), 2)]

class PatchSplitter:
    SECTION_SPLITS = 'diff --git'

    def __init__(self, repo_name, commit, parent_commit, patch_section=PatchSection):
        self.repo_name = repo_name
        self.commit = commit
        self.parent_commit = parent_commit
        self.patch_section = PatchSection

    def split_by_diff_section(self, patch):
        diff_sections = [section for section in patch.split(self.SECTION_SPLITS) if section]

        disassembled_patch = []

        for diff_section in diff_sections:
            patch_section = self.patch_section(
                    repo_name=self.repo_name,
                    section=diff_section,
                    commit=self.commit,
                    parent_commit=self.parent_commit)

            disassembled_patch.append(patch_section)

        return disassembled_patch

    def all_modified_methods(self, patches):
        modified_methods = [patch.modified_methods for patch in patches]

        return [mm for mm in modified_methods if mm]

class PatchReader:
    patches=0
    ps=0
    patch =0

    def __init__(self, project, commitId1, commitId2):
        self.patch = get_patch(project, commitId1, commitId2)
        self.ps = PatchSplitter(project, commitId1, commitId2)
        self.patches = self.ps.split_by_diff_section(self.patch)

    def methods(self):
        methods = self.ps.all_modified_methods(self.patches)
        return methods

if __name__ == '__main__':
    commit_1 = '39fb8c4666d7462c38bf36d4a16ecc50bce61204'
    commit_2 = 'c14dd4f5153caaa4c2ed9d45c3573a279bae553e'

    patch = get_patch(
            'hbase',
            commit_1,
            commit_2)

    ps = PatchSplitter('hbase',
            commit_1,
            commit_2)

    patches = ps.split_by_diff_section(patch)
    methods = ps.all_modified_methods(patches)

    import pdb; pdb.set_trace()
    print(methods)
