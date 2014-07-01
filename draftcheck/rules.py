import re
import functools
from helpers import join_patterns

RULES_LIST = []

BAD_PHRASES = [
    'as to whether', 'the case that', 'in many cases', 'certainly',
    'is a (man|woman) who', 'along (the same|these|this|the) (lines|line)', 
    'One of the most', 'absolutely essential', 'a large number of',
    'all intents and purposes', 'not important', 'the question as to whether',
    'there is no doubt but that', 'this is a (subject|topic) which',
    'the fact that', 'the authors', 'the author', 'more and more', 'over and over',
    'reason to believe', 'is used to', 'in regards to', 'while at the same time',
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

REDUNDANT_PHRASES = [
    'end result', 'final outcome', 'already exists', 'and also', 'at about',
    'clearly evident', '(join|group) together', 'revert back', 'repeat the same',
    'the reason is because'
]

class RuleCategory:
    """General rules that do not fit in any other category."""
    General = 0

    """Rules regarding typographic errors or best practices."""
    Type = 1

    """Rules regarding compositional style and usage."""
    Style = 2

def rule(pattern=None, category=RuleCategory.General, show_spaces=False, \
         in_env='paragraph'):
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
            return []

        wrapper.__id = len(RULES_LIST) + 1
        wrapper.show_spaces = show_spaces
        wrapper.__doc__ = func.__doc__
        RULES_LIST.append(wrapper)

        return wrapper
    return inner_rule

type_rule = functools.partial(rule, category=RuleCategory.Style)
style_rule = functools.partial(rule, category=RuleCategory.Style)

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
    """Unnecessary, overused or needlessly wordy. Consider rephrasing."""
    return [m.span() for m in matches]

@style_rule(join_patterns(WEASEL_WORDS))
def check_weasel_words(text, matches):
    """Weasel words should be avoided."""
    return [m.span() for m in matches]

@style_rule(r'\b(am|are|were|being|is|been|was|be)\s(\w+ed|{0})'.format(join_patterns(IRREGULAR_VERBS)))
def check_passive_voice(text, matches):
    """Passive voice should be avoided."""
    return [m.span() for m in matches]

@type_rule('\s-\s')
def check_space_surrounded_dash(text, matches):
    """A dash surrounded by a space should be an em-dash: '---'."""
    return [m.span() for m in matches]

@style_rule(r'\bnot\s(un|in)[a-z]+(ed|ble|ing|ent|thy)\b')
def check_double_negative(text, matches):
    """Avoid double negatives."""
    return [m.span() for m in matches]

@style_rule(r'\b([a-z]+)\s([a-z]+)\b(?![^{]*})')
def check_duplicate_word(text, matches):
    """Remove duplicated word."""
    return [m.span() for m in matches if m.group(1) == m.group(2)]

@style_rule(r'\b((does|did)\snot|doesn\'t|didn\'t)\s(\w+)')
def check_negatives(text, matches):
    """Negatives should be rephrases as affirmatives."""
    return [m.span() for m in matches]

@style_rule(r'\.\s(And|But)\b')
def check_begin_with_add_or_but(text, matches):
    """Sentences should not begin with 'And' or 'But'."""
    return [m.span() for m in matches]

@style_rule(r'\. There (is|are)\b')
def check_begin_with_there_is(text, matches):
    """Sentences should not begin with 'There is' or 'There are'."""
    return [m.span() for m in matches]

@style_rule(r'\bmore\s\w+er\b')
def check_double_comparative(text, matches):
    """Comparative adjectives should not be preceded by 'more'."""
    return [m.span() for m in matches]

@style_rule(join_patterns(REDUNDANT_PHRASES))
def check_redundant_expressions(text, matches):
    """Redundant expressions should be rephrased."""
    return [m.span() for m in matches]


def validate(text, env='paragraph'):
    for r in RULES_LIST:
        for match in r(text, env):
            yield r, match

def get_brief(rule):
    return rule.__doc__.split('\n\n')[0]

def get_detail(rule):
    return rule.__doc__.split('\n\n')[1:]
