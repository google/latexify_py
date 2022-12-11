from typing import Any

from latexify import exceptions


def convert_constant(value: Any) -> str:
    """Helper to convert constant values to LaTeX.

    Args:
        value: A constant value.

    Returns:
        The LaTeX representation of `value`.
    """
    if value is None or isinstance(value, bool):
        return r"\mathrm{" + str(value) + "}"
    if isinstance(value, (int, float, complex)):
        # TODO(odashi): Support other symbols for the imaginary unit than j.
        return str(value)
    if isinstance(value, str):
        return r'\textrm{"' + value + '"}'
    if isinstance(value, bytes):
        return r"\textrm{" + str(value) + "}"
    if value is ...:
        return r"\cdots"
    raise exceptions.LatexifyNotSupportedError(
        f"Unrecognized constant: {type(value).__name__}"
    )
