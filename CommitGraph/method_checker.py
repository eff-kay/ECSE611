import re

class MethodChecker:
    CHECKS = [
        'has_one_set_of_brackets',
        'is_not_new_or_private_public',
        'module_dot_name_with_brackets',
        'is_not_for_loop_or_boolean_operator',
        'is_not_class',
    ]

    def __init__(self, potential):
        self.potential = potential
        self._is_method = None

    @property
    def is_method(self):
        if self._is_method is None:
            self._is_method = self._check()

        return self._is_method

    def __bool__(self):
        return self.is_method

    @property
    def method_signature(self):
        if not self.is_method:
            return None

        method = re.search(r'[\w|\.]+\(.*\)', self.potential).group()

        return method

    def _check(self):
        if not self.potential:
            return False

        for check in self.CHECKS:
            method = getattr(self, check)
            if not method():
                return False

        return True

    def has_one_set_of_brackets(self):
        # one set is not necessary, since they can be a half line
        return self.potential.count('(') >= 1

    def is_not_new_or_private_public(self):
        match = re.search(r'(\w+)\s[\w|\.]+\(.*\)', self.potential)

        if not match:
            return True

        if match.group(1) in ['new', 'private', 'public']:
            return False

        return True

    def module_dot_name_with_brackets(self):
        match = re.search(r'[\w|\.]+\(.*\)', self.potential)

        return bool(match)

    def is_not_for_loop_or_boolean_operator(self):
        match = re.search(r'([\w|\.]+)\(.*\)', self.potential)

        if match.group(1) in ['if', 'for', 'or', 'not', 'equals', 'add', 'delete']:
            return False

        return True

    def is_not_class(self):
        match = re.search(r'([\w|\.]+)\(.*\)', self.potential)

        if not match:
            return True

        g = match.group(1)

        if ',' in g:
            klass, name = g.split('.')

            if klass.isupper():
                return True

            if klass[0].isupper():
                return False

        if g.isupper():
            return True

        if g[0].isupper() and not g[1].isupper():
            return False

        return True
