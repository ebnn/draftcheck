from nose.tools import assert_true, assert_false

import draftcheck

def found_error(rule, text):
    for r, _ in draftcheck.validate(text):
        if r.__id == rule.__id:
            return True
    return False

def test_space_before_footnote():
    assert_true(found_error(draftcheck.check_space_before_footnote,
            r'Bake the cake at 150 degrees \footnote{Degrees celsius}'))
    assert_false(found_error(draftcheck.check_space_before_footnote,
            r'Bake the cake at 150 degrees\footnote{Degrees celsius}'))

def test_cite_after_period():
    assert_true(found_error(draftcheck.check_cite_after_period,
            r'Napoleonic war.\cite{smith08}'))
    assert_false(found_error(draftcheck.check_cite_after_period,
            r'Napoleonic war\cite{smith08}.'))

def test_cite_used_as_noun():
    assert_true(found_error(draftcheck.check_cite_used_as_noun,
            r'This is shown in \cite{smith08}'))
    assert_false(found_error(draftcheck.check_cite_used_as_noun,
            r'It is shown to be this way \cite{smith08}.'))

def test_no_space_before_cite():
    assert_true(found_error(draftcheck.check_no_space_before_cite,
            r'Napoleonic war\cite{smith08}.'))
    assert_true(found_error(draftcheck.check_no_space_before_cite,
            r'Napoleonic war \cite{smith08}.'))
    assert_false(found_error(draftcheck.check_no_space_before_cite,
            r'Napoleonic war~\cite{smith08}.'))
