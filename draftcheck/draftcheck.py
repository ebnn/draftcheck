#!/bin/python

import re
from rules import validate, get_brief, get_detail

LATEX_ENVS = {
    'math': ['math', 'array', 'eqnarray', 'equation', 'align'],
    'paragraph': ['abstract', 'document', 'titlepage']
}

LATEX_ENVS = dict((k, env) for env in LATEX_ENVS for k in LATEX_ENVS[env])

def pad_string(text, span, size):
    left_str = text[max(0, span[0] - size):span[0]]
    right_str = text[span[1]:min(len(text), span[1] + size)]

    text_format = '{0}{1}{2}'

    if len(left_str) == size:
        text_format = '...' + text_format

    if len(right_str) == size:
        text_format = text_format + '...'

    padded_str = text_format.format(left_str, text[span[0]:span[1]], right_str)
    start_index = len(left_str) + (3 if len(left_str) == size else 0)

    return padded_str, start_index

def check_line(lineno, line, span, env, args):
    """Check a line for rule violations and prints information to stdout.

    Parameters
    ----------
    lineno : int
        The number of the line of text to check.

    line : str
        The line of text to check.

    span : tuple(int, int)
        The start and end index to check.

    env : str
        The current LaTeX environment.

    args : dict
        The program arguments.

    Returns
    -------
    num_errors : int
        The number of mistakes in the line.
    """
    num_errors = 0

    for r, match in validate(line[span[0]:span[1]], env):
        match = (match[0] + span[0], match[1] + span[0])

        prefix = '{0}:{1}:{2}:'.format('file', lineno, match[0])
        print prefix,

        padded_str, start_index = pad_string(line, match, 10)
        if r.show_spaces:
            print padded_str.replace(' ', '_')
        else:
            print padded_str

        print ' ' * (len(prefix) + start_index + 1) + '^' * (match[1] - match[0])
        print "\t[R{0:03d}]".format(r.__id), get_brief(r)
        print

        num_errors += 1

    return num_errors

def main(args):
    # Count the total number of errors
    num_errors = 0

    # Regular expressions to extract environments
    env_begin_regex = re.compile(r'\\begin{(\w+)}')
    env_end_regex = re.compile(r'\\end{(\w+)}')
    math_env_regex = re.compile(r'(?:\$\$|\$|\\\[)(.+?)(?:\$\$|\$|\\\])')

    for filename in args.filenames:
        with open(filename, 'r') as infile:
            # Initialise the environment stack
            envs = ['paragraph']

            for lineno, line in enumerate(infile):
                # Check if the environment has changed
                match = env_begin_regex.match(line)
                if match:
                    envs.append(LATEX_ENVS.get(match.group(1), 'unknown'))

                match = env_end_regex.match(line)
                if match:
                    envs.pop()

                chunks = math_env_regex.split(line)
                if len(chunks) == 1:
                    num_errors += check_line(lineno + 1, chunks[0],
                            (0, len(chunks[0])), envs[-1], args)
                else:
                    offset = 0
                    for text_chunk, math_chunk in zip(chunks[::2], chunks[1::2]):
                        num_errors += check_line(lineno + 1, text_chunk,
                                (offset, offset + len(text_chunk)), envs[-1], args)
                        offset += len(text_chunk)

                        num_errors += check_line(lineno + 1, math_chunk,
                                (offset, offset + len(math_chunk)), 'math', args)
                        offset += len(math_chunk)

    print
    print 'Total of {0} mistakes found.'.format(num_errors)

if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
            description='Check for common mistakes in LaTeX documents.')
    parser.add_argument('filenames', action='append', \
            help='List of filenames to check')

    args = parser.parse_args()
    main(args)
