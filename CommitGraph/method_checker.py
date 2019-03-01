import re

class MethodChecker:
    CHECKS = [
        'has_one_set_of_brackets',
        'has_method_definition',
        'has_formal_arguments',
    ]

    def __init__(self, potential):
        self.potential = potential

    @property
    def is_method(self):
        if not self.potential:
            return False

        for check in self.CHECKS:
            if not getattr(self, check)():
                return False

        return True

    @property
    def method_signature(self):
        method = re.search(r'(\s*\w+\([\w|\s]+[,$|\)])', self.potential).group()
        if method.endswith(','):
            method += ' ...)'
        return method

    def __bool__(self):
        return self.is_method

    def has_one_set_of_brackets(self):
        # one set is not necessary, since they can be a half line
        return self.potential.count('(') == 1

    def has_method_definition(self):
        potential_method = re.search(r'(\s*\w+)\(', self.potential)

        if not potential_method:
            return False

        method_definition = potential_method\
            .group()\
            .rstrip('(')\
            .lstrip(' ') # just in case

        try:
            length_of_match = re.match(r'\w+', method_definition).span()[1]
        except AttributeError:
            return False

        result = length_of_match == len(method_definition)

        return result

    def has_formal_arguments(self):
        # include support for half lines
        argument = re.search(r'\(([\s|\w]+)[,$|\)]', self.potential)

        if not argument:
            return False

        arguments = [a for a in argument.group().rstrip(')').lstrip('(').split(',') if a]
        arguments = [tuple([a for a in args.split(' ') if a]) for args in arguments if args]

        for a in arguments:
            if len(a) == 1:
                return False

            if '"' in a:
                return False

        return True

