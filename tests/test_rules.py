from nose.tools import assert_true, assert_false

import draftcheck.rules as rules
import draftcheck.validator as validator

def found_error(rule, text):
    print text
    for r, _ in validator.Validator().validate(text):
        if r.__id == rule.__id:
            print r.__doc__
            return True
    return False

def normalise_text(text):
    return ' '.join(map(lambda x: x.lstrip(), text.split('\n')))

def test_examples():
    import re

    example_regex = re.compile(r'(Good|Bad):\n(.+?)(?:\n\n|\s*$)', flags=re.S)
    for rule in rules.RULES_LIST:
        for match in example_regex.finditer(rule.__doc__):
            expected = False if match.group(1) == 'Good' else True
            text = normalise_text(match.group(2))

            yield check_example, rule, text, expected

def check_example(r, text, expected):
    if expected is True:
        assert_true(found_error(r, text), msg=text)
    else:
        assert_false(found_error(r, text), msg=text)
