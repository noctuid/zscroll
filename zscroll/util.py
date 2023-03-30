"""Zscroll utility functions."""

import shlex
from collections import deque
from dataclasses import dataclass, is_dataclass
from subprocess import CalledProcessError, check_output
from unicodedata import east_asian_width


# https://github.com/tiangolo/typer/issues/197
def inject_dataclass_args(dclass):
    """Use dataclass as an argument instead of individual options/arguments with typer."""
    assert is_dataclass(dclass)  # noqa: S101

    def decorator(func):
        @dataclass
        class Wrapped(dclass):
            """Create a class that inherits from dclass and run func in the post init method."""

            def __post_init__(self):
                if hasattr(super, '__post_init__'):
                    super().__post_init__()
                func(self)

        Wrapped.__doc__ = func.__doc__

        return Wrapped

    return decorator


def shell_output(command: str, shell: bool = False) -> str | None:
    """Get the output of a shell command as a string.

    If the command fails, return None.  This is useful in certain cases where a
    command may not work initially but will work later so that zscroll does not
    need to be restarted (e.g. an mpc command fails because mpd is not yet
    running).

    :param command: the command to run
    :return: the command output
    """
    try:
        return (
            check_output(command if shell else shlex.split(command), shell=shell)
            .decode(encoding='UTF-8')
            .rstrip('\n')
        )
    except CalledProcessError:
        return None


def visual_len(text: str) -> int:
    """Determine the "visual" length of text.

    Halfwidth characters are counted as length 1 and fullwidth characters are
    counted as length 2.

    :param text: the text to examine
    :return: the visual length of the text
    """
    visual_length = 0
    for char in text:
        width = east_asian_width(char)
        if width in ('W', 'F'):
            visual_length += 2
        else:
            visual_length += 1
    return visual_length


def visual_slice(text: str, index: int, length: int) -> str:
    """Return a text slice starting at index of the given length.

    Halfwidth characters are counted as length 1 and fullwidth characters are counted as length 2.
    If the text is shorter than the given length, pad it with spaces at the end.

    :param text: the text to slice
    :param index: the character index to start at
    :param length: the "visual" length of the text slice to return
    :return: the text slice
    """
    # can't use slicing alone since different characters have different "visual length"
    text_deque = deque(text[index:] + text[:index])
    text = ''
    while length > 0 and len(text_deque) > 0:
        char = text_deque.popleft()
        next_length = visual_len(char)
        if next_length == 2 and length == 1:
            text += ' '
            return text
        text += char
        length -= next_length
    # this case can only happen when moving from scrolling text to shorter fixed text; pad with
    # spaces at end to cover old text when printing in place
    if length > 0:
        text += ' ' * length
    return text
