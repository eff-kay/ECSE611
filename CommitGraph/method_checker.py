import re

class MethodChecker:
    CHECKS = [
        'has_one_set_of_brackets',
        'is_not_new',
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

        method = re.search(r'\w+\(.*\)', self.potential).group()

        return method

    def _check(self):
        if not self.potential:
            return False

        for check in self.CHECKS:
            if not getattr(self, check)():
                return False

        return True

    def has_one_set_of_brackets(self):
        # one set is not necessary, since they can be a half line
        return self.potential.count('(') == 1

    def is_not_new(self):
        match = re.match(r'(\w+)\s\w+\(.*\)', self.potential)

        if not match:
            return False

        if match.group(1) == 'new':
            return False

        return True
