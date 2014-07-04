import re
import functools
from helpers import join_patterns

RULES_LIST = []

def rule(pattern=None, show_spaces=False, in_env='paragraph'):
    """Decorator used to create rules.

    Parameters
    ----------
    pattern : string, optional
        If specified, pattern is treated as a regular expression and the result
        of calling `finditer` on the text being checked is passed to the wrapped
        function.

    show_spaces : boolean
        Whether the output should replace whitespace with underscores
        (in order to clearly indicate errors involving whitespace). Defaults to
        false.
    """
    regexpr = re.compile(pattern)

    def inner_rule(func):
        def wrapper(text, env):
            if in_env == 'all' or env == in_env:
                return func(text, regexpr.finditer(text))
            return []

        wrapper.__id = len(RULES_LIST) + 1
        wrapper.show_spaces = show_spaces
        wrapper.in_env = in_env
        wrapper.__doc__ = func.__doc__

        RULES_LIST.append(wrapper)

        return wrapper
    return inner_rule

@rule(r'\s+\\footnote{', show_spaces=True)
def check_space_before_footnote(text, matches):
    """Do not precede footnotes with spaces.

    Remove the extraneous spaces before the \\footnote command.

    Examples
    --------
    Bad:
        Napolean's armies were defeated in Waterloo \\footnote{In present day
        Belgium}.

    Good:
        Napolean's armies were defeated in Waterloo\\footnote{In present day
        Belgium}.
    """
    return [m.span() for m in matches]

@rule(r'\.\\cite{')
def check_cite_after_period(text, matches):
    """Place citations before periods with a non-breaking space.

    Move the \\cite command inside the sentence, before the period.

    Examples
    --------
    Bad:
        Johannes Brahms was born in Hamburg.\\cite{}

    Good:
        Johannes Brahms was born in Hamburg~\\cite{}.
    """
    return [m.span() for m in matches]

@rule(r'\b(:?in|as|on|by)[ ~]\\cite{')
def check_cite_used_as_noun(text, matches):
    """Avoid using citations as nouns.

    Examples
    --------
    Bad:
        The method proposed in~\\cite{} shows a decrease in methanol toxicity.

    Good:
        A proposed method shows a decrease in methanol toxicity~\\cite{}.
    """
    return [m.span() for m in matches]

@rule(r'[^~]\\cite{')
def check_no_space_before_cite(text, matches):
    """Place a single, non-breaking space '~' before citations.

    Examples
    --------
    Bad:
        Apollo 17's "The Blue Marble" \\cite{} photo of the Earth became an icon
        in the environmental movement.

    Good:
        Apollo 17's "The Blue Marble"~\\cite{} photo of the Earth became an icon
        in the environmental movement.
    """
    return [m.span() for m in matches]

@rule(r'\d+%')
def check_unescaped_percentage(text, matches):
    """Escape percentages with backslash.

    Examples
    --------
    Bad:
        The company's stocks rose by 15%.

    Good:
        The company's stocks rose by 15\\%.
    """
    return [m.span() for m in matches]

@rule(r'\s[,;.!?]', show_spaces=True)
def check_space_before_punctuation(text, matches):
    """Do not precede punctuation characters with spaces.
    
    Example
    -------
    Bad:
        Nether Stowey, where Coleridge wrote The Rime of the Ancient Mariner ,
        is a few miles from Bridgewater.

    Good:
        Nether Stowey, where Coleridge wrote The Rime of the Ancient Mariner,
        is a few miles from Bridgewater.
    """
    return [m.span() for m in matches]

@rule(r'\w+\(|\)\w+', show_spaces=True)
def check_no_space_next_to_parentheses(text, matches):
    """Separate parentheses from text with a space.

    Example
    -------
    Bad:
        I went to his house yesterday(my third attempt to see him).

    Good:
        I went to his house yesterday (my third attempt to see him).
    """
    return [m.span() for m in matches]

@rule(r'\d+\s?x\d+')
def check_incorrect_usage_of_x_as_times(text, matches):
    """In the context of 'times', use $\\times$ instead of 'x'.
    
    Example
    -------
    Bad:
        We used an 10x10 grid for the image filter.

    Good:
        We used an $10 \\times 10$ grid for the image filter.
    """
    return [m.span() for m in matches]

@rule('[a-z]+\s-\s[a-z]+')
def check_space_surrounded_dash(text, matches):
    """Use an em-dash '---' to denote parenthetical breaks or statements.
    
    Example
    -------
    Bad:
        He only desired one thing - success.

    Good:
        He only desired one thing --- success.
    """
    return [m.span() for m in matches]

@rule(r'\b(\w+)\s+\1\b(?![^{]*})')
def check_duplicate_word(text, matches):
    """Remove duplicated word.

    Example
    -------
    Bad:
        The famous two masks associated with drama are symbols of the
        the ancient Muses, Thalia (comedy) and Melpomene (tragedy).

    Good:
        The famous two masks associated with drama are symbols of the
        ancient Muses, Thalia (comedy) and Melpomene (tragedy).
    """
    return [m.span() for m in matches]

@rule(r'\.\.\.')
def check_dot_dot_dot(text, matches):
    """Typeset ellipses by \\ldots, not '...'.

    Example
    -------
    Bad:
        New York, Tokyo, Budapest, ...

    Good:
        New York, Tokyo, Budapest, \\ldots
    """
    return [m.span() for m in matches]

@rule(r'"')
def check_double_quote(text, matches):
    """Use left and right quotation marks `` and '' rather than ".

    Example
    -------
    Bad:
        "Very much indeed," Alice said politely.

    Good:
        ``Very much indeed,'' Alice said politely.
    """
    return [m.span() for m in matches]

@rule(r"(?: |^)(``|`)|(''|')(?: |$)")
def check_unmatched_quotes(text, matches):
    """Left quotes must be balanced by a matching right quote.

    Example
    -------
    Bad:
        ``Very much indeed,' Alice said politely.

    Bad:
        ``Very much indeed, Alice said politely.

    Good:
        ``Very much indeed,'' Alice said politely.
    """
    unmatched = []
    for m in matches:
        if m.group(1) is not None:
            # Opening quote
            unmatched.append(m)
        else:
            if len(unmatched) == 0:
                yield m.span()
            else:
                if unmatched[-1].group(1) == '`' and m.group(2) == "''":
                    yield unmatched[-1].span()
                elif unmatched[-1].group(1) == '``' and m.group(2) == "'":
                    yield unmatched[-1].span()

                unmatched.pop()

    for m in unmatched:
        yield m.span()

@rule(r'\\begin{center}', in_env='all')
def check_begin_center(text, matches):
    """Use \\centering instead of \\begin{center}.

    Example
    -------
    Bad:
        \\begin{figure}
            \\begin{center}
                \\includegraphics
            \\end{center}
        \\end{figure}

    Good:
        \\begin{figure}
            \\centering
            \\includegraphics
        \\end{figure}
    """
    return [m.span() for m in matches]

@rule(r'^\$\$', in_env='math')
def check_double_dollar_math(text, matches):
    """Use \[ or \\begin{equation} instead of $$.

    Example
    -------
    Bad:
        $$ 1 + 1 = 2 $$

    Good:
        \\[ 1 + 1 = 2 \\]

    Good:
        \\begin{equation}
            1 + 1 = 2
        \\end{equation}
    """
    return [m.span() for m in matches]

@rule(r'\d\s?-\s?\d')
def check_numeric_range_dash(text, matches):
    """Use endash '--' for numeric ranges instead of hyphens.

    Example
    -------
    Bad:
        A description of medical practices at the time are on pages 17-20.

    Good:
        A description of medical practices at the time are on pages 17--20.
    """
    return [m.span() for m in matches]

@rule(r'\\footnote{.+?}[,;.?]')
def check_footnote_before_punctuation(text, matches):
    """Place footnotes after punctuation marks."""
    return [m.span() for m in matches]

@rule(r'\b(<|>)\b')
def check_relational_operators(text, matches):
    """Use \\langle and \\rangle instead of '<' and '>' for angle brackets."""
    return [m.span() for m in matches]

@rule(r'\\cite{.+?}\s?\\cite{')
def check_multiple_cite(text, matches):
    """Use \\cite{..., ...} for multiple citations."""
    return [m.span() for m in matches]

@rule(r'\d(m|A|kg|s|K|mol|cd)\b')
def check_number_next_to_unit(text, matches):
    """Place a non-breaking space between a number and its unit."""
    return [m.span() for m in matches]

def get_brief(rule):
    return rule.__doc__.split('\n\n')[0]

def get_detail(rule):
    return rule.__doc__.split('\n\n')[1]
