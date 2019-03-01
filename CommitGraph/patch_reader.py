import os
import subprocess
import re
import itertools
import operator
import copy

# I really don't have time to fix this
try:
    from method_checker import MethodChecker
    from method_getter import MethodGetter
    from repo_executor import RepoExecutor
except ModuleNotFoundError:
    from .method_checker import MethodChecker
    from .method_getter import MethodGetter
    from .repo_executor import RepoExecutor


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
        return [chunk.changed_methods() for chunk in self.chunks]

    def _split_into_pairs(self, l):
        return [l[i:i+2] for i in range(0, len(l), 2)]

class Change:
    INVALID_CHANGES = [
        r'^[</|<].*>', # xml
        r'^import',
        r'^package',
        r'^\*',
        r'^/\**',
        r'^@.*', # @overrides are not direct changes to methods,
        r'^[transient|final]',
        r'\sclass\s',
    ]

    METHOD_STARTS = [
        r'^[private|public]',
    ]

    def __init__(self,
            changeline,
            changes,
            filename,
            commit,
            parent_commit,
            repo_name,
            getter=MethodGetter):

        self.changeline = changeline
        self.changes = [change for change in changes.split('\n') if change]
        self.filename = filename

        self.commit = commit
        self.parent_commit = parent_commit
        self.repo_name = repo_name

        self.getter = getter(
                changeline=self.changeline,
                filename=self.filename,
                commit=commit,
                parent_commit=parent_commit,
                repo_name=repo_name)

    @property
    def has_valid_changes(self):
        valid_changed_lines = self._valid_changed_lines()

        if not valid_changed_lines:
            return (False, None)

        return (True, valid_changed_lines)

    def changed_methods(self):
        valid, changed_lines = self.has_valid_changes

        if not valid:
            return []

        method_names = []

        for grouped_changes in self.group(changed_lines):

            line = self.__strip_diffmarkers(grouped_changes[0][1])
            check = MethodChecker(line)

            # print(f'looking at {line} with RESULT {check.is_method}')
            if not check.is_method:
                print(f'Need to search source code for {grouped_changes}')
                method_or_class_name = self.getter.get(grouped_changes)

                if not method_or_class_name: # we tried our best
                    continue

                method_names.append(method_or_class_name)
                continue

            method_name = check.method_signature

            if not method_name:
                continue

            method_names.append(method_name)

        return method_names

    def group(self, linenumbers_with_changes):
        groups = []

        def relative_change(enumerable):
            index, change = enumerable
            value = change[0]
            return value - index

        for _, gens in itertools.groupby(
                enumerate(linenumbers_with_changes),
                relative_change):
            groups.append(list(map(operator.itemgetter(1), gens)))
        return groups

    def _valid_changed_lines(self):
        valid_changed_lines = []
        for i, line in self._get_changed_lines():
            if self._invalid_change(line):
                continue

            valid_changed_lines.append((i, line))
        return valid_changed_lines

    def _invalid_change(self, line):
        line = self.__strip_diffmarkers(line)

        if not line:
            return True

        for regex in self.INVALID_CHANGES:
            if re.search(regex, line):
                return True

        return False

    def _get_changed_lines(self):
        return [(i, line) for i, line in enumerate(self.changes) if line[0] in ['+', '-']]

    def __strip_diffmarkers(self, line):
        return copy.copy(line)[1:].lstrip(' ')

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
        methods = [patch.modified_methods for patch in patches]
        # double nested
        return set(itertools.chain(*itertools.chain(*methods)))

if __name__ == '__main__':

    patch = get_patch(
            'hbase',
            'f0032c925510877396b1b0979abcc2ce83e67529',
            '482b505796e1dfe33551c1d20af2ff9d1d6a38dc')

    ps = PatchSplitter('hbase',
            'f0032c925510877396b1b0979abcc2ce83e67529',
            '482b505796e1dfe33551c1d20af2ff9d1d6a38dc')

    patches = ps.split_by_diff_section(patch)
    methods = ps.all_modified_methods(patches)
