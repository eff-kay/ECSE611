import os
import subprocess

try:
    from method_checker import MethodChecker
    from class_checker import ClassChecker
    from repo_executor import RepoExecutor
except ModuleNotFoundError:
    from .method_checker import MethodChecker
    from .class_checker import ClassChecker
    from .repo_executor import RepoExecutor

class CodeReader:
    def __init__(self,
            lines,
            method_checker=MethodChecker,
            class_checker=ClassChecker):

        self.lines = lines
        self.method_checker = method_checker
        self.class_checker = class_checker

    def indentation(self, line):
        return len(line) - len(line.lstrip(' '))

    def indented_lines(self):
        counted_indentation_lines = []

        for line in self.lines.split("\n"):
            indentation = self.indentation(line)
            counted_indentation_lines.append((indentation, line))

        return counted_indentation_lines

    def method_owner(self, line, source_file_changeline):
        line = line.lstrip('+-')
        line_indentation = self.indentation(line)

        indented_lines = self.indented_lines()
        # we can use index with ranges to improve performance

        try:
            line_index = self.lines.split("\n").index(
                line,
                source_file_changeline[0],
                sum(source_file_changeline))
        except ValueError:
            # sometimes the file does not exist
            # this can occur when we get the commit-id wrong
            # i'm not sure why this is the case
            return {}

        current_indentation = indented_lines[line_index][0]
        for line in reversed(indented_lines[:line_index]):

            line_indentation = line[0]
            if line_indentation >= current_indentation or not line[1]:
                continue

            method_checker = self.method_checker(line[1])
            class_checker = self.class_checker(line[1])

            if (not method_checker) and (not class_checker):
                current_indentation = line[0]
                continue

            if method_checker:
                return method_checker.method_signature

            if class_checker:
                return class_checker.class_signature

class MethodGetter:

    def __init__(self,
            changeline,
            filename,
            commit,
            parent_commit,
            repo_name,
            code_reader=CodeReader,
            executor=RepoExecutor):

        self._changeline = changeline
        self.filename = filename

        self.commit = commit
        self.parent_commit = parent_commit
        self.repo_name = repo_name

        self.code_reader = code_reader
        self.executor = executor(self.repo_name)

    def get(self, lines):
        """
        We have to first:
        1. go to the repo
        2. checkout the base commit
        3. head the first N lines
        4. iterating from the bottom line upwards, find the method
        5. Once the method has been found, we find the block that represents
        the class
        6. iterating over every line in the class, return {class_name:
        [methods_called]}
        7. return method
        """
        topmost_line = lines[0][1]

        operation = topmost_line[0]
        commit_hash, changeline = self.operator_aware_commit_changeline(operation)
        lines_with_method = self.get_n_lines(commit_hash, changeline)

        code_reader = self.code_reader(lines_with_method)

        return code_reader.method_owner(topmost_line, changeline)

    def operator_aware_commit_changeline(self, operation):
        # disclaimer: this appears to work, but it reads counter-intuitive
        if operation == '-':
            return self.commit, self.changeline['source_file']

        if operation == '+':
            return self.parent_commit, self.changeline['target_file']

        raise NotImplementedError('This is not a changeline!')

    @property
    def changeline(self):
        source_file, target_file = self._changeline\
                .rstrip(' ')\
                .lstrip(' ')\
                .split(' ')

        def to_int(f):
            return [abs(int(i)) for i in f.split(',')]

        changeline = {
            'source_file': to_int(source_file),
            'target_file': to_int(target_file),
        }

        return changeline

    def get_n_lines(self, commit, changeline):
        maximum_depth = sum(changeline)

        self.executor.execute(f'git checkout {commit} --quiet')
        output = self.executor.execute(f'head -n {maximum_depth} {self.filename}')

        # just make sure to clean up
        self.executor.execute(f'git checkout master --quiet')

        return output

if __name__ == '__main__':
    m = MethodGetter(
            changeline=' -160,6 +160,7 ',
            filename='hbase-http/src/main/java/org/'\
                    'apache/hadoop/hbase/http/jmx/JMXJsonServlet.java',
            commit='f0032c925510877396b1b0979abcc2ce83e67529',
            parent_commit='482b505796e1dfe33551c1d20af2ff9d1d6a38dc',
            repo_name='hbase',
            )

    lines_with_method = m.get_n_lines()
