ADJECTIVE_SUFFIXES = [
    'able', 'ac', 'al', 'ancy', 'ant', 'ard', 'ary', 'ate',
    'ative', 'atory', 'ed', 'ent', 'er', 'est', 'ful', 'ial',
    'ible', 'ic', 'ical', 'ized', 'ised', 'ier', 'ily', 'ing',
    'ion', 'ional', 'ious', 'ish', 'ist', 'tic', 'ite', 'itory', 'ive', 'less',
    'ory', 'ous', 'ual', 'thy'
]

def is_adjective(word):
    return any(word.endswith(suffix) for suffix in ADJECTIVE_SUFFIXES)
