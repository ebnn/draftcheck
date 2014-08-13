draftcheck
==========

`draftcheck` is an LaTeX linter that is specifically designed for academic writing.

Installation
------------

`draftcheck` can be manually installed from source:

```bash
mkdir draftcheck && cd draftcheck
git clone https://github.com/ebnn/draftcheck.git
python setup.py install
```

Usage
-----

The supplied files contains several example LaTeX files that can be used to test it.

```bash
$ draftcheck examples/article.tex
```