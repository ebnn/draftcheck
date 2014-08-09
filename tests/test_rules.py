from nose.tools import assert_equals
from draftcheck.validator import Validator
import draftcheck.rules as rules


def found_error(rule, text):
    """Return whether a particular rule has been violated."""
    for r, _ in Validator().validate(text):
        if r.id == rule.id:
            print r.__doc__
            return True
    return False


def normalise_text(text):
    """Replace newlines and surrounding whitespace with a single space."""
    return ' '.join(map(lambda x: x.lstrip(), text.split('\n')))


def test_examples():
    """A test generator that creates tests from examples in rule docstrings."""
    import re

    example_regex = re.compile(r'(Good|Bad):\n(.+?)(?:\n\n|\s*$)', flags=re.S)
    for rule in rules.RULES_LIST:
        for match in example_regex.finditer(rule.__doc__):
            expected = False if match.group(1) == 'Good' else True
            text = normalise_text(match.group(2))

            yield assert_equals, found_error(rule, text), expected
