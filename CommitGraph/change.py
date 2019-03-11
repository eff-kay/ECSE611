import re
import copy
import collections

try:
    from method_getter import MethodGetter
    from function_checker import FunctionChecker
    from class_checker import ClassChecker
    from method_checker import MethodChecker
except ModuleNotFoundError:
    from .method_getter import MethodGetter
    from .function_checker import FunctionChecker
    from .class_checker import ClassChecker
    from .method_checker import MethodChecker

class Change:
    INVALID_CHANGES = [
        r'^[</|<].*>', # xml
        r'^import',
        r'^package',
        r'^\*',
        r'^/\**',
        r'^@.*', # @overrides are not direct changes to methods,
    ]

    METHOD_STARTS = [
        r'^[private|public|protected]',
    ]

    ChangedLine = collections.namedtuple(
            'ChangedLine',
            [
                'line', # the diff line
                'signature', # the method or the class name
                'change_type', # 'class' or 'method'
                'operation', # + or -
                'line_number' # absolute location of the diff line within the file
            ])

    LabelledLine = collections.namedtuple(
            'LabelledLine',
            ['line', 'modified']
    )

    def __init__(self,
            changeline,
            changes,
            filename,
            commit,
            parent_commit,
            repo_name,
            getter=MethodGetter,
            function_checker=FunctionChecker,
            class_checker=ClassChecker,
            method_checker=MethodChecker,
            ):

        self.changeline = changeline
        self.changes = [change for change in changes.split('\n')]
        self.filename = filename

        self.commit = commit
        self.parent_commit = parent_commit
        self.repo_name = repo_name

        self.function_checker = function_checker
        self.class_checker = class_checker
        self.method_checker = method_checker

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

    def __changeline(self):
        def to_int(changeline):
            return [abs(int(c)) for c in source_file_changeline.split(',')]

        changeline = self.changeline.lstrip(' ').rstrip(' ')
        source_file_changeline, target_file_changeline = changeline.split(' ')
        sf_starts_at, sf_total = to_int(source_file_changeline)
        tf_starts_at, tf_total = to_int(target_file_changeline)

        return sf_starts_at, sf_total, tf_starts_at, tf_total

    def changed_methods_and_classes(self):
        valid, changed_lines = self.has_valid_changes

        unlabelled = {}

        if not valid:
            return unlabelled

        for change_line in changed_lines:
            if change_line.change_type == 'class':
                unlabelled.update({ change_line.signature: {} })
                continue

            if change_line.change_type == 'method':
                class_signature = self.getter.get_class(change_line)

                if class_signature is None:
                    print(f'{change_line} was unable to be found')
                    continue

                unlabelled = self.merge(unlabelled, class_signature)

        labelled = {}
        self.line_only_changed_lines = [cl.signature for cl in changed_lines]
        for klass, functions in unlabelled.items():

            funcs = {}
            for function, methods in functions.items():
                meths = set([self.convert_to_labelled_line(method) for method in methods])
                func = self.convert_to_labelled_line(function, any([lmethod.modified for lmethod in meths]))
                funcs.update({func: meths})

            k = self.convert_to_labelled_line(klass)
            labelled.update({k: funcs})

        return labelled

    def convert_to_labelled_line(self, line, is_modified=None):
        return self.LabelledLine(line=line, modified=is_modified or (line in self.line_only_changed_lines))

    def merge(self, original, class_signature):
        for klass, methods_calls in class_signature.items():
            if klass not in original:
                original[klass] = methods_calls
                continue

            for methods, calls in methods_calls.items():
                if methods not in original[klass]:
                    original[klass][methods] = set(calls)
                    continue

                original[klass][methods] = original[klass][methods].union(calls)

        return original

    def _valid_changed_lines(self):
        valid_changed_lines = []

        # if the starts_at is the same
        changeline = self.__changeline()
        starts_at = changeline[0]

        for relative_line_number, line in self._get_changed_lines():
            operation, line = self.__strip_diffmarkers(line)

            if not line:
                continue

            if self._blatently_invalid_changes(line):
                continue

            def check(line):
                function_checker = self.function_checker(line)
                method_checker = self.method_checker(line)
                class_checker = self.class_checker(line)

                if not any([class_checker, function_checker, method_checker]):
                    return None, None

                if class_checker:
                    return class_checker.class_signature, 'class'

                if function_checker:
                    return function_checker.function_signature, 'function'

                if method_checker:
                    return method_checker.method_signature, 'method'

            signature, change_type = check(line)

            if signature is None:
                continue

            changed_line = self.ChangedLine(
                line=line,
                signature=signature,
                change_type=change_type,
                operation=operation,
                line_number=starts_at - 1 + relative_line_number - 1
            )

            valid_changed_lines.append(changed_line)

        return valid_changed_lines

    def _blatently_invalid_changes(self, line):
        for regex in self.INVALID_CHANGES:
            if re.search(regex, line):
                return True

        return False

    def _get_changed_lines(self):
        lines = [(i, line) for i, line in enumerate(self.changes)]
        return [l for l in lines if l[1] and l[1][0] in ['+', '-']]

    def __strip_diffmarkers(self, line):
        return line[0], copy.copy(line)[1:].lstrip(' ')



