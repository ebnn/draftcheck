"""This modules contains code to find rule violations in text."""

import rules
import itertools
import re

# Different LaTeX environments
LATEX_ENVS = {
    'math': ['math', 'array', 'eqnarray', 'equation', 'align'],
    'paragraph': ['abstract', 'document', 'titlepage']
}

LATEX_ENVS = dict((k, env) for env in LATEX_ENVS for k in LATEX_ENVS[env])


def validate(text, env='paragraph'):
    """Validate a particular piece of text.

    This function finds rules that are violated by the text.

    Parameters
    ----------
    text : string
        The text to validate.
    env : string
        The LaTeX environment type. This is used for environment sensitive
        rules. Defaults to 'paragraph'.
    """
    for rule in rules.RULES_LIST:
        for span in rule(text, env):
            yield rule, span


class Validator(object):
    # Regular expressions to extract environments
    env_begin_regex = re.compile(r'\\begin{(\w+)}')
    env_end_regex = re.compile(r'\\end{(\w+)}')
    math_env_regex = re.compile(r'((?:\$\$|\$|\\\[).+?(?:\$\$|\$|\\\]))')

    def __init__(self):
        # Initialise the environment stack
        self._envs = ['paragraph']

    def validate(self, line):
        # Check if the environment has changed
        match = Validator.env_begin_regex.match(line)
        if match:
            self._envs.append(LATEX_ENVS.get(match.group(1), 'unknown'))

        match = Validator.env_end_regex.match(line)
        if match:
            self._envs.pop()

        if self._envs[-1] == 'math':
            # Because we are already in maths mode, there is no need to detect
            # nested math environments.
            chunks = ['', line]
        else:
            # Split the text into chunks of 'text' and 'math'
            chunks = Validator.math_env_regex.split(line)

        chunk_envs = itertools.cycle([self._envs[-1], 'math'])

        offset = 0
        for chunk, chunk_env in zip(chunks, chunk_envs):
            for rule, span in validate(chunk, chunk_env):
                offsetted_span = (span[0] + offset, span[1] + offset)
                yield rule, offsetted_span

            offset += len(chunk)
