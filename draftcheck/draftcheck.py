import re

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

def main(path, flags):
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

            for r, match in validate(line, envs[-1], flags):
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

    main(sys.argv[1], { 'pedantic': False })
