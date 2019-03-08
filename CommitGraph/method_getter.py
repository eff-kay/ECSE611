import os
import subprocess

try:
    from function_checker import FunctionChecker
    from class_checker import ClassChecker
    from method_checker import MethodChecker
    from repo_executor import RepoExecutor
except ModuleNotFoundError:
    from .function_checker import FunctionChecker
    from .class_checker import ClassChecker
    from .method_checker import MethodChecker
    from .repo_executor import RepoExecutor

class LineNotFoundError(Exception): pass;

class Finder:
    def __init__(self,
            target_file,
            function_checker=FunctionChecker,
            class_checker=ClassChecker,
            method_checker=MethodChecker,
            ):

        self.lines = self.indented_lines(target_file)
        self.function_checker = function_checker
        self.class_checker = class_checker
        self.method_checker = method_checker

    def indentation(self, line):
        return len(line) - len(line.lstrip(' '))

    def indented_lines(self, target_file):
        counted_indentation_lines = []

        for line in target_file.split("\n"):
            indentation = self.indentation(line)
            line = line.lstrip(' ').rstrip(' ')
            counted_indentation_lines.append((indentation, line))

        return counted_indentation_lines

    def method_owner(self, change_line):
        current_indentation = None

        for line in self.lines[change_line.line_number::-1]:
            if current_indentation is None:
                current_indentation = line[0]

            line_indentation = line[0]
            if line_indentation >= current_indentation or not line[1]:
                continue

            class_checker = self.class_checker(line[1])

            if not class_checker:
                current_indentation = line[0]
                continue

            # we've found the top level class here
            methods = self.all_calls_in_class(line)
            return {class_checker.class_signature: methods}

    def all_calls_in_class(self, line_with_indentation):
        current_function = None
        current_method = None

        index = self.lines.index(line_with_indentation)
        class_indentation_level = line_with_indentation[0]

        methods = {}
        for line in self.lines[index+1:]:
            indentation, text = line

            if indentation == 0 and not text:
                # we've hit on newline
                continue

            if indentation == class_indentation_level and text:
                # we've hit on the closing brackets, hopefully
                break

            if self.class_checker(text):
                # we're somehow in another class
                break

            function_checker = self.function_checker(text)
            method_checker = self.method_checker(text)

            if function_checker:
                signature = function_checker.function_signature
                methods.update({signature: set()})
                current_function = signature
                continue

            if method_checker and current_function is not None:
                # we're inside a function
                signature = method_checker.method_signature
                methods[current_function].add(signature)
                continue

        return methods

class MethodGetter:
    def __init__(self,
            changeline,
            filename,
            commit,
            parent_commit,
            repo_name,
            finder=Finder,
            executor=RepoExecutor):

        self._changeline = changeline
        self.filename = filename

        self.commit = commit
        self.parent_commit = parent_commit
        self.repo_name = repo_name

        self.executor = executor(self.repo_name)

        self.commit_file = self.get_file(self.commit)
        self.parent_file = self.get_file(self.parent_commit)

        self.finder = finder

    def get_class(self, change_line):
        target_file = self.operation_aware_choose_file(change_line.operation)

        try:
            owner = self.finder(target_file).method_owner(change_line)
        except LineNotFoundError:
            owner = self.finder(self.opposite_file).method_owner(change_line)
        except LineNotFoundError: # we got nothing
            owner = None

        return owner

    def operation_aware_choose_file(self, operation):
        if operation == '-':
            self.opposite_file = self.commit_file
            return self.parent_file

        if operation == '+':
            self.opposite_file = self.parent_file
            return self.commit_file

    def get_file(self, commit):
        return self.executor.execute_commands([
            f'git checkout --force {commit} --quiet',
            f'cat {self.filename}',
            # f'git checkout --force master --quiet',
        ]).stdout.decode('utf-8')

if __name__ == '__main__':
    m = Finder(
            changeline=' -160,6 +160,7 ',
            filename='hbase-http/src/main/java/org/'\
                    'apache/hadoop/hbase/http/jmx/JMXJsonServlet.java',
            commit='f0032c925510877396b1b0979abcc2ce83e67529',
            parent_commit='482b505796e1dfe33551c1d20af2ff9d1d6a38dc',
            repo_name='hbase',
            )

    lines_with_method = m.get_n_lines()
