"""Exceptions used in Latexify."""


class LatexifyError(Exception):
    """Base class of all Latexify exceptions.

        Subclasses of this exception does not mean incorrect use of the library by the user,
    <<<<<<< HEAD
        but informs users that Latexify went into something worng during compiling the given
    =======
        but informs users that Latexify went into something wrong during compiling the given
    >>>>>>> main
        functions.
        These functions are usually captured by the frontend functions (e.g., `with_latex`)
        to prevent destroying the entire program.
        Errors caused by the wrong inputs should raise built-in exceptions.
    """

    ...


class LatexifyNotSupportedError(LatexifyError):
    """Some subtree in the AST is not supported by the current implementation.

    This error is raised when the library discovered incompatible syntaxes due to lack
    of the implementation. Possibly this error would be resolved in the future.
    """

    ...


class LatexifySyntaxError(LatexifyError):
    """Some subtree in the AST is not supported.

    This error is raised when the library discovered syntaxes that are not possible to
    be processed anymore. This error is essential, and wouldn't be resolved in the
    future.
    """

    ...
