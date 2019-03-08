import re

class ClassChecker:
    CHECKS = [
        'has_keyword_class',
    ]

    def __init__(self, potential):
        self.potential = potential
        self._is_class = None

    @property
    def is_class(self):
        if self._is_class is None:
            self._is_class = self._check()

        return self._is_class

    def _check(self):
        if not self.potential:
            return False

        for check in self.CHECKS:
            if not getattr(self, check)():
                return False

        return True

    @property
    def class_signature(self):
        if not self.is_class:
            return None

        match = re.search(r'.*class\s([A-Z]\w+)', self.potential)

        if match is not None:
            return match.group()
        else:
            return None

    def __bool__(self):
        return self.is_class

    def has_keyword_class(self):
        return re.match(r'.*\s*class\s.*', self.potential)
