from rules import get_brief
from validator import Validator


def pad_string(text, span, size):
    left_str = text[max(0, span[0] - size):span[0]]
    right_str = text[span[1]:min(len(text), span[1] + size)]

    text_format = '{0}{1}{2}'

    if len(left_str) == size:
        text_format = '...' + text_format

    if len(right_str) == size:
        text_format += '...'

    padded_str = text_format.format(left_str, text[span[0]:span[1]], right_str)
    start_index = len(left_str) + (3 if len(left_str) == size else 0)

    return padded_str, start_index


def print_warning(fname, lineno, line, span, rule, args):
    prefix = '{0}:{1}:{2}:'.format(fname, lineno, span[0])
    print prefix,

    padded_str, start_index = pad_string(line, span, 10)
    if rule.show_spaces:
        print padded_str.replace(' ', '_')
    else:
        print padded_str

    print ' ' * (len(prefix) + start_index + 1) + '^' * (span[1] - span[0])
    print "\t[{0:03d}]".format(rule.id), get_brief(rule)
    print


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Check for common mistakes in LaTeX documents.')

    parser.add_argument('filenames', action='append',
                        help='List of filenames to check')

    args = parser.parse_args()

    # Count the total number of errors
    num_errors = 0

    for fname in args.filenames:
        with open(fname, 'r') as infile:
            validator = Validator()
            for lineno, line in enumerate(infile):
                for rule, span in validator.validate(line):
                    print_warning(fname, lineno, line.strip(), span, rule, args)
                    num_errors += 1

    if num_errors > 0:
        print '\nTotal of {0} mistakes found.'.format(num_errors)
        return 1
    else:
        print 'No mistakes found.'
        return 0