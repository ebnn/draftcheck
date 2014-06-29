import re
import functools

RULES_LIST = []

BAD_PHRASES = [
    'as to whether', 'the case that', 'in many cases', 'certainly',
    'is a (man|woman) who', 'along (the same|these|this|the) (lines|line)', 
    'One of the most', 'absolutely essential', 'a large number of',
    'all intents and purposes', 'not important', 'the question as to whether',
    'there is no doubt but that', 'this is a (subject|topic) which',
    'the fact that', 'the authors', 'the author', 'revert back', 'repeat the same',
    'reason to believe', 'join together', 'is used to', 'in regards to',
    'importantly', 'as long as', 'along (those|these) lines', '(a|the) tendency to',
    '(a|the) need for', '(a|the) majority of'
]

WEASEL_WORDS = [
    'many','various','very','fairly','several','extremely',
    'exceedingly','quite','remarkably','few','surprisingly',
    'mostly','largely','huge','tiny','(are|is) a number',
    'excellent','interestingly','significantly',
    'substantially','clearly','vast','relatively','completely'
]

IRREGULAR_VERBS = [
    'awoken', 'been', 'born', 'beat', 'become', 'begun', 'bent',
    'beset', 'bet', 'bid', 'bidden', 'bound', 'bitten', 'bled', 'blown', 'broken',
    'bred', 'brought', 'broadcast', 'built', 'burnt', 'burst',
    'bought', 'cast', 'caught', 'chosen', 'clung', 'come',
    'cost', 'crept', 'cut', 'dealt', 'dug', 'dived',
    'done', 'drawn', 'dreamt', 'driven', 'drunk', 'eaten', 'fallen',
    'fed', 'felt', 'fought', 'found', 'fit', 'fled', 'flung', 'flown',
    'forbidden', 'forgotten', 'foregone', 'forgiven',
    'forsaken', 'frozen', 'gotten', 'given', 'gone',
    'ground', 'grown', 'hung', 'heard', 'hidden', 'hit',
    'held', 'hurt', 'kept', 'knelt', 'knit', 'known', 'laid', 'led',
    'leapt', 'learnt', 'left', 'lent', 'let', 'lain', 'lighted',
    'lost', 'made', 'meant', 'met', 'misspelt', 'mistaken', 'mown',
    'overcome', 'overdone', 'overtaken', 'overthrown', 'paid', 'pled', 'proven',
    'put', 'quit', 'read', 'rid', 'ridden', 'rung', 'risen', 'run', 'sawn', 'said',
    'seen', 'sought', 'sold', 'sent', 'set', 'sewn', 'shaken', 'shaven',
    'shorn', 'shed', 'shone', 'shod', 'shot', 'shown', 'shrunk', 'shut',
    'sung', 'sunk', 'sat', 'slept', 'slain', 'slid', 'slung', 'slit',
    'smitten', 'sown', 'spoken', 'sped', 'spent', 'spilt', 'spun', 'spit',
    'split', 'spread', 'sprung', 'stood', 'stolen', 'stuck', 'stung', 'stunk',
    'stridden', 'struck', 'strung', 'striven', 'sworn', 'swept',
    'swollen', 'swum', 'swung', 'taken', 'taught', 'torn', 'told', 'thought',
    'thrived', 'thrown', 'thrust', 'trodden', 'understood', 'upheld',
    'upset', 'woken', 'worn', 'woven', 'wed', 'wept', 'wound', 'won',
    'withheld', 'withstood', 'wrung', 'written'
]

LATEX_ENVS = {
    'math': ['math', 'array', 'eqnarray', 'equation', 'align'],
    'paragraph': ['abstract', 'document', 'titlepage']
}

LATEX_ENVS = dict((k, env) for env in LATEX_ENVS for k in LATEX_ENVS[env])

class RuleCategory:
    """General rules that do not fit in any other category."""
    General = 0

    """Rules regarding typographic errors or best practices."""
    Type = 1

    """Rules regarding compositional style and usage."""
    Style = 2

def rule(pattern=None, category=RuleCategory.General, show_spaces=False, in_env='paragraph'):
    """Decorator used to create rules.

    Parameters
    ----------
    pattern : string, optional
        If specified, pattern is treated as a regular expression and the result
        of calling `finditer` on the text being checked is passed to the wrapped
        function.

    category : `RuleCategory`, optional
        Represents the category of this rule. Rules with the same category
        are grouped together. Defaults to RuleCategory.General.

    show_spaces : boolean
        Whether the output should replace whitespace with underscores
        (in order to clearly indicate errors involving whitespace). Defaults to
        false.
    """
    regexpr = re.compile(pattern)

    def inner_rule(func):
        def wrapper(text, env):
            if env == in_env:
                return func(text, regexpr.finditer(text))
            else:
                return []

        wrapper.__id = len(RULES_LIST) + 1
        wrapper.show_spaces = show_spaces
        wrapper.__doc__ = func.__doc__
        RULES_LIST.append(wrapper)

        return wrapper
    return inner_rule

type_rule = functools.partial(rule, category=RuleCategory.Style)
style_rule = functools.partial(rule, category=RuleCategory.Style)

def join_patterns(patterns):
    """Join several regular expression patterns together with 'or's.
    
    Parameters
    ----------
    patterns : a list or iterable of strings
        Contains the patterns to be joined together into one regular expression.
    """
    return r'\b(' + '|'.join(map(lambda x: '(?:' + x + ')', patterns)) + ')'

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

@type_rule(r'\s+\\footnote{', show_spaces=True)
def check_space_before_footnote(text, matches):
    """There should not be any spaces before footnotes."""
    return [m.span() for m in matches]

@type_rule(r'\.\\cite{')
def check_cite_after_period(text, matches):
    """Citations should appear before periods, not after."""
    return [m.span() for m in matches]

@style_rule(r'(:?in|as|on|by)\s\\cite{')
def check_cite_used_as_noun(text, matches):
    """Citations should not be used as nouns."""
    return [m.span() for m in matches]

@type_rule(r'[^~]\\cite{')
def check_no_space_before_cite(text, matches):
    """Citations should be preceded by a single, non-breaking space '~'."""
    return [m.span() for m in matches]

@type_rule(r'\d+%')
def check_unescaped_percentage(text, matches):
    """Percentage signs should be escaped."""
    return [m.span() for m in matches]

@type_rule(r'\s[,;.!?]', show_spaces=True)
def check_space_before_punctuation(text, matches):
    """Punctuation characters should not be preceded by a space."""
    return [m.span() for m in matches]

@type_rule(r'\d+\s?x\d+')
def check_incorrect_usage_of_x_as_times(text, matches):
    """In the context of 'times', use $\\times$ instead of 'x'"""
    return [m.span() for m in matches]

@style_rule(join_patterns(BAD_PHRASES))
def check_bad_phrases(text, matches):
    """Redundant, unnecessary, overused or needlessly wordy. Consider rephrasing."""
    return [m.span() for m in matches]

@style_rule(join_patterns(WEASEL_WORDS))
def check_weasel_words(text, matches):
    """Weasel words should be avoided."""
    return [m.span() for m in matches]

@style_rule(r'\b(am|are|were|being|is|been|was|be)\s(\w+ed|{0})'.format(join_patterns(IRREGULAR_VERBS)))
def check_passive_tense(text, matches):
    """Passive tense should be avoided."""
    return [m.span() for m in matches]

@type_rule('\s-\s')
def check_space_surrounded_dash(text, matches):
    """A dash surrounded by a space should be an em-dash: '---'."""
    return [m.span() for m in matches]

@style_rule(r'\bnot\sun')
def check_double_negative(text, matches):
    """Avoid double negatives."""
    return [m.span() for m in matches]

@style_rule(r'\b([a-z]+)\s([a-z]+)\b(?![^{]*})')
def check_duplicate_word(text, matches):
    """Remove duplicated word."""
    return [m.span() for m in matches if m.group(1) == m.group(2)]

def validate(text, env='paragraph'):
    for r in RULES_LIST:
        for match in r(text, env):
            yield r, match

def main(path):
    num_errors = 0
    envs = ['paragraph']
    env_begin_regex = re.compile(r'\\begin{(\w+)}')
    env_end_regex = re.compile(r'\\end{(\w+)}')

    with open(path, 'r') as infile:
        for lineno, line in enumerate(infile):
            # Check if the environment has changed
            match = env_begin_regex.match(line)
            if match:
                envs.append(LATEX_ENVS.get(match.group(1), 'unknown'))

            match = env_end_regex.match(line)
            if match:
                envs.pop()

            for r, match in validate(line, envs[-1]):
                prefix = '{0}:{1}:{2}:'.format('file', lineno, match[0])
                print prefix,

                padded_str, start_index = pad_string(line, match, 10)
                if r.show_spaces:
                    print padded_str.replace(' ', '_')
                else:
                    print padded_str

                print ' ' * (len(prefix) + start_index + 1) + '^' * (match[1] - match[0])
                print "\t[R{0:03d}]".format(r.__id), r.__doc__
                print

                num_errors += 1

    print
    print 'Total of {0} warnings found.'.format(num_errors)

if __name__ == '__main__':
    import sys

    main(sys.argv[1])
