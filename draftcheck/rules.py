"""This module contains rule definitions."""

import re

# Global rules list to store all the registered rules
RULES_LIST = []


def rule(pattern, show_spaces=False, in_env='paragraph'):
    """Decorator used to create rules.

    The decorated function must have the following signature:
        def example_rule(text, matches):
            return ...

    where `text` is the string that needs to be checked, and matches is the
    result of calling `re.finditer(pattern, text)`, i.e. the `MatchObject`s
    representing substrings that match the specified regex pattern.

    The decorated function must return a list of tuple pairs, where each tuple
    pair (start, end) represents the start and end indices of substrings in
    `text` that violate the rule.

    Parameters
    ----------
    pattern : string
        If specified, pattern is treated as a regular expression and the result
        of calling `finditer` on the text being checked is passed to the wrapped
        function.
    show_spaces : boolean, optional
        Whether the output should replace whitespace with underscores
        (in order to clearly indicate errors involving whitespace). Defaults to
        false.
    in_env : string, optional
        The LaTeX environment in which this rule can be applied. Only text in
        the specified environment are checked against this rule. This may be
        set to 'any' if this rule applies in any environment. Defaults to
        'paragraph'.
    """
    regexpr = re.compile(pattern)

    def inner_rule(func):
        def wrapper(text, env):
            if in_env == 'any' or env == in_env:
                return func(text, regexpr.finditer(text))
            return []

        # Store the parameters in the function as attributes
        wrapper.id = len(RULES_LIST) + 1
        wrapper.show_spaces = show_spaces
        wrapper.in_env = in_env

        # Inherit the docstring from the function
        wrapper.__doc__ = func.__doc__

        # Add it to our global rules list
        RULES_LIST.append(wrapper)

        return wrapper
    return inner_rule


def rule_generator(show_spaces=False, in_env='paragraph'):
    """Decorator that generates rules from a generator."""
    def inner_rule(func):
        for r in func():
            # Register this rule into our global rules list
            @rule(pattern=r[0], show_spaces=show_spaces, in_env=in_env)
            def generated_rule(_, matches):
                return [m.span() for m in matches]

            # Format the docstring with parameters specific to this instance
            # of the rule
            RULES_LIST[-1].__doc__ = func.__doc__.format(*r[1:])
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
        Apollo 17's ``The Blue Marble'' \\cite{} photo of the Earth became an
        icon of the environmental movement.

    Good:
        Apollo 17's ``The Blue Marble''~\\cite{} photo of the Earth became an
        icon of the environmental movement.
    """
    return [m.span() for m in matches]


@rule(r'[^~]\\ref{')
def check_no_space_before_ref(text, matches):
    """Place a single, non-breaking space '~' before references.

    Examples
    --------
    Bad:
        The performance of the engine is shown in Figure \\ref{}.

    Good:
        The performance of the engine is shown in Figure~\\ref{}.
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
        Pablo Picasso(1881--1973) is one of the pioneers of Cubism.

    Good:
        Pablo Picasso (1881--1973) is one of the pioneers of Cubism.
    """
    return [m.span() for m in matches]


@rule(r'\d+\s?x\d+')
def check_incorrect_usage_of_x_as_times(text, matches):
    """In the context of 'times' or 'multiply', use $\\times$ instead of 'x'.
    
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


@rule(r'\b([a-z]+)\s+\1\b(?![^{]*})')
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


@rule(r'\s\'.+?\'[\s\.,]')
def check_single_quote(text, matches):
    """Use left and right quotation marks ` and ' rather than '.

    Example
    -------
    Bad:
        It is 'too good to be true'.

    Good:
        It is `too good to be true'.
    """
    return [m.span() for m in matches]


@rule(r'\\begin{center}', in_env='any')
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
    """Place footnotes after punctuation marks.

    Example
    -------
    Bad:
        \emph{Waiting for Godot}\\footnote{First performed on 5 January 1953 in
        Paris}, written by Samuel Beckett, is an example of Absurdist Theatre.

    Good:
        \emph{Waiting for Godot},\\footnote{First performed on 5 January 1953 in
        Paris} written by Samuel Beckett, is an example of Absurdist Theatre.
    """
    return [m.span() for m in matches]


@rule(r'<[^\s](.+?)[^\s]>', in_env='math')
def check_relational_operators(text, matches):
    """Use \\langle and \\rangle instead of '<' and '>' for angle brackets.

    Example
    -------
    Bad:
        Inner product of $a$ and $b$ is denoted by $<a, b>$.

    Good:
        Inner product of $a$ and $b$ is denoted by $\\langle a, b \\rangle$.

    Good:
        It must satisfy this inequality: $a < b, c > d$.
    """
    return [m.span() for m in matches]


@rule(r'\\cite{.+?}\s?\\cite{')
def check_multiple_cite(text, matches):
    """Use \\cite{..., ...} for multiple citations.

    Example
    -------
    Bad:
        This problem has many real-world applications~\\cite{A}\\cite{B}.

    Good:
        This problem has many real-world applications~\\cite{A, B}.
    """
    return [m.span() for m in matches]


@rule(r'\d(m|A|kg|s|K|mol|cd)\b')
def check_number_next_to_unit(text, matches):
    """Place a non-breaking space between a number and its unit.

    Example
    -------
    Bad:
        We measured the distance travelled by the ball to be 14.5m.

    Good:
        We measured the distance travelled by the ball to be 14.5~m.
    """
    return [m.span() for m in matches]


@rule(r'[^\\](sin|cos|tan|log|max|min)', in_env='math')
def check_unescaped_named_math_operators(text, matches):
    """Precede named mathematical operators with a backslash.

    Example
    -------
    Bad:
        The famous trignometric identity: $sin^2(x) + cos^2(x) = 1$.

    Good:
        The famous trignometric identity: $\\sin^2(x) + \\cos^2(x) = 1$.
    """
    return [m.span() for m in matches]


@rule(r'\b(e\.g\.|i\.e\.)\s+')
def check_abbreviation_innerword_spacing(text, matches):
    """Place a '\\ ' (backslash space) after the period of an abbreviation.

    Example
    -------
    Bad:
        This shows that new technological gadgets, e.g. smart phones, decrease
        the attention span of young adults.

    Good:
        This shows that new technological gadgets, e.g.\\\\ smart phones,
        decrease the attention span of young adults.
    """
    return [m.span() for m in matches]


@rule(r'\\def\\[a-z]+{')
def check_def_command(text, matches):
    """Do not use the \\def command. Use \\newcommand instead."""
    return [m.span() for m in matches]


@rule(r'\\sloppy')
def check_sloppy_command(text, matches):
    """Avoid the \\sloppy command."""
    return [m.span() for m in matches]


@rule(r"'''|```")
def check_triple_quote(text, matches):
    """Use a thin space \, to separate quotes."""
    return [m.span() for m in matches]


@rule(r'1st|2nd|3rd')
def check_unspelt_ordinal_numbers(text, matches):
    """Spell out ordinal numbers (1st, 2nd, etc.) in words."""
    return [m.span() for m in matches]


@rule(r'[a-z]+ \d [a-z]+')
def check_unspelt_single_digit_numbers(text, matches):
    """Spell out single digit numbers in words."""
    return [m.span() for m in matches]


@rule(r',\s*\.\.\.\s*,', in_env='math')
def check_dot_dot_dot_maths(text, matches):
    """Use \\cdots to denote ellipsis in maths."""
    return [m.span() for m in matches]


@rule(r'(?<!\\url{)(\bhttps?://)[^\s.]+\.[-A-Za-z0-9+&@#/%?=~_|!:,.;]+')
def check_bare_urls(text, matches):
    """Wrap URLs with the \\url command."""
    return [m.span() for m in matches]


@rule(r'\.  [A-Z]')
def check_double_space(text, matches):
    """Prefer single space over double space after a period."""
    return [m.span() for m in matches]


@rule_generator()
def check_incorrect_abbreviations():
    """Punctuate abbreviations correctly. Should be "{0}"."""

    changes = {
        r'et\. al\.': 'et al.',
        r'etc[^\.]': 'etc.',
        r'i\.e[^\.]': 'i.e.',
        r'e\.g[^\.]': 'e.g.',
        r'Dr\.': 'Dr',
    }

    for incorrect, correct in changes.items():
        yield r'\b' + incorrect + r'\b', correct


@rule_generator()
def check_obsolete_commands():
    """Use the \\{0} command instead."""

    changes = {
        'rm': 'textrm',
        'tt': 'texttt',
        'it': 'textit',
        'bf': 'textbf',
        'sc': 'textsc',
        'sf': 'textsf',
        'sl': 'textsl',
        'over': 'frac',
        'centerline': 'centering'
    }

    for incorrect, correct in changes.items():
        yield '\\' + incorrect + '{', correct


@rule_generator()
def check_obsolete_packages():
    """Avoid obsolete packages. Use {0} instead."""

    changes = {
        'a4': 'a4paper',
        'a4wide': 'a4paper',
        't1enc': '\usepackage[T1]{fontenc}',
        'umlaute': '\usepackage[latin1]{inputenc}',
        'isolatin': '\usepackage[isolatin]{inputenc}',
        'isolatin1': '\usepackage[latin1]{inputenc}',
        'fancyheadings': 'fancyhdr',
        'mathptm': 'mathptmx',
        'mathpple': 'mathpazo',
        'epsf': 'graphicx',
        'epsfig': 'graphicx',
        'doublespace': 'setspace',
        'scrpage': 'scrpage2'
    }

    for incorrect, correct in changes.items():
        yield '\\' + incorrect + '{', correct


@rule_generator()
def check_obsolete_environments():
    """Use the {0} instead."""

    changes = {
        'eqnarray': '"align" environment',
        'appendix': '\\appendix command'
    }

    for incorrect, correct in changes.items():
        yield '\\begin{' + incorrect + '}', correct


def get_brief(r):
    return r.__doc__.split('\n\n')[0]