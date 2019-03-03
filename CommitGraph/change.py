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
        r'^[private|public]',
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

    def __init__(self,
            changeline,
            changes,
            filename,
            commit,
            parent_commit,
            repo_name,
            getter=MethodGetter,
            function_checker=FunctionChecker,
            class_checker=ClassChecker):

        self.changeline = changeline
        self.changes = [change for change in changes.split('\n')]
        self.filename = filename

        self.commit = commit
        self.parent_commit = parent_commit
        self.repo_name = repo_name

        self.function_checker = function_checker
        self.class_checker = class_checker

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

        methods = {'called': {}, 'modified': {}}

        if not valid:
            return methods

        for change_line in changed_lines:
            if change_line.change_type == 'class':
                methods['modified'].update({ change_line.signature: [] })

            if change_line.change_type == 'method':
                class_signature = self.getter.get_class(change_line)

                if class_signature is None:
                    print(f'{change_line} was unable to be found')
                    continue

                klass = [s for s in class_signature.keys()][0]

                if klass not in methods['modified']:
                    methods['modified'][klass] = [change_line.signature]
                else:
                    methods['modified'][klass].append(change_line.signature)

                methods['called'].update(class_signature)

        return methods

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

            function_checker = self.function_checker(line)
            class_checker = self.class_checker(line)

            if (not function_checker.is_function) and (not class_checker.is_class):
                continue

            signature = class_checker.class_signature or function_checker.function_signature

            change_type = 'class' if class_checker else 'method'

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
