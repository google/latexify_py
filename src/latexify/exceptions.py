"""Exceptions used in Latexify."""


class LatexifyError(Exception):
    """Base class of all Latexify exceptions.

    Subclasses of this exception does not mean incorrect use of the library by the user,
    but informs users that Latexify went into something worng during compiling the given
    functions.
    These functions are usually captured by the frontend functions (e.g., `with_latex`)
    to prevent destroying the entire program.
    Errors caused by the wrong inputs should raise built-in exceptions.
    """

    ...


class LatexifyNotSupportedError(LatexifyError):
    """Some subtree in the AST is not supported by the current implementation."""

    ...


class LatexifySyntaxError(LatexifyError):
    """Some subtree in the AST has an incompatible form to be converted to LaTeX."""

    ...
