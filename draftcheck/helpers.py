def join_patterns(patterns):
    """Join several regular expression patterns together with 'or's.
    
    Parameters
    ----------
    patterns : a list or iterable of strings
        Contains the patterns to be joined together into one regular expression.
    """
    return r'\b(' + '|'.join(map(lambda x: '(?:' + x + ')', patterns)) + ')'
