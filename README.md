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
$ draftcheck examples/simple.tex
examples/simple.tex:26:1: (http://www.comp.leeds.ac.uk/andyr/misc/latex/\-latextut...
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	[030] Wrap URLs with the \url command.

examples/simple.tex:31:37: ...thin \LaTeX\cite{lamport94}...
                                        ^^^^^^^
	[004] Place a single, non-breaking space '~' before citations.

examples/simple.tex:49:19: ...n 'itemize' environmen...
                                        ^^
	[014] Left quotes must be balanced by a matching right quote.

examples/simple.tex:93:0: \begin{center}
                          ^^^^^^^^^^^^^^
	[015] Use \centering instead of \begin{center}.
```