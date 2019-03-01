import re

class ClassChecker:
    CHECKS = [
        'has_keyword_class',
    ]

    def __init__(self, potential):
        self.potential = potential

    @property
    def is_class(self):
        if not self.potential:
            return False

        for check in self.CHECKS:
            if not getattr(self, check)():
                return False

        return True

    @property
    def class_signature(self):
        return re.search(r'.*class\s([A-Z]\w+)', self.potential).group()

    def __bool__(self):
        return self.is_class

    def has_keyword_class(self):
        return re.match(r'.*\s*class\s.*', self.potential)
