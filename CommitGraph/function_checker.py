import re

class FunctionChecker:
    CHECKS = [
        'has_one_set_of_brackets',
        'has_function_definition',
        'has_formal_arguments',
        'has_not_semicolon_at_end',
    ]

    def __init__(self, potential):
        self.potential = potential
        self._is_function = None

    @property
    def is_function(self):
        if self._is_function is None:
            self._is_function = self._check()

        return self._is_function

    def _check(self):
        if not self.potential:
            return False

        for check in self.CHECKS:
            if not getattr(self, check)():
                return False

        return True

    @property
    def function_signature(self):
        if not self.is_function:
            return None

        function = re.search(r'(\s*\w+\(.+[,$|\)])', self.potential).group()

        if function.endswith(','):
            function += ' ...)'
        return function

    def __bool__(self):
        return self.is_function

    def has_one_set_of_brackets(self):
        # one set is not necessary, since they can be a half line
        return self.potential.count('(') == 1

    def has_function_definition(self):
        potential_function = re.search(r'(\s*\w+)\(', self.potential)

        if not potential_function:
            return False

        function_definition = potential_function\
            .group()\
            .rstrip('(')\
            .lstrip(' ') # just in case

        try:
            length_of_match = re.match(r'\w+', function_definition).span()[1]
        except AttributeError:
            return False

        result = length_of_match == len(function_definition)

        return result

    def has_formal_arguments(self):
        # include support for half lines
        argument = re.search(r'\(([\s\w<>,]+)[,$|\)]', self.potential)

        if not argument:
            return False

        argument = argument.group().lstrip('(').rstrip(')')

        if re.search(r'Map<.*>\s(.*)', argument):
            return True

        arguments = [a for a in argument.split(',') if a]
        arguments = [tuple([a for a in args.split(' ') if a]) for args in arguments if args]

        for a in arguments:
            if len(a) == 1:
                return False

            if '"' in a:
                return False

        return True

    def has_not_semicolon_at_end(self):
        return self.potential[-1] != ';'
