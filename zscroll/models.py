"""Zscroll data models."""
import sys
from dataclasses import dataclass
from types import EllipsisType
from typing import Optional

import typer


def get_stdin_if_available() -> str | EllipsisType:
    """Return stdin text if there is any.

    Otherwise return ..., which typer.Arguments uses to denote a required argument.

    :return: stdin string or ...
    """
    return ... if sys.stdin.isatty() else sys.stdin.read()


def validate_length(ctx: typer.Context, value: int | None):
    """Validate --length.

    Require it to be positive.

    :return: then length if non-negative
    :raises typer.BadParameter: if the length is negative
    """
    if ctx.resilient_parsing:
        # fix completion
        return None

    if value is not None and value < 0:
        length_error_message = "Must be positive"
        raise typer.BadParameter(length_error_message)
    return value


def validate_match_options(
    ctx: typer.Context, value: list[tuple[str, str]]
) -> list[tuple[str, str]] | None:
    """Validate --match-text (and --match-command).

    When only 1 match command was specified, rewrite the list of commands to match again to have the
    same length as the match text/setting pairs.  Otherwise, require both to be the same length.

    :return: a list of (match/search text, "<new flags>") or None
    :raises typer.BadParameter: if the length of match commands is invalid
    """
    if ctx.resilient_parsing:
        # fix completion
        return None
    match_commands = ctx.params.get('match_command', [])
    if len(match_commands) == 1:
        ctx.params['match_command'] = [match_commands[0] for _ in range(len(value))]
    elif len(match_commands) != len(value):
        match_error_message = "Number of -M / --match-command uses must be 1 or match -m"
        raise typer.BadParameter(match_error_message)
    return value


@dataclass()
class GlobalOptions:
    """Zscroll command flags that apply globally (i.e. can only be specified once)."""

    reverse: bool = typer.Option(
        False,
        '--reverse',
        '-r',
        is_flag=False,
        help="whether to scroll the text from left to right",
    )
    newline: bool = typer.Option(
        True,
        '--newline',
        '-n',
        is_flag=False,
        help="print a newline after each update; printing a newline may be necessary for panels ",
    )
    delay: float = typer.Option(
        0.4,
        '--delay',
        '-d',
        help="delay in seconds for scrolling updates; lower this for faster scrolling",
    )
    timeout: float = typer.Option(
        0,
        '--timeout',
        '-t',
        help="time in seconds to wait before exiting; 0 means don't exit",
    )
    max_shift_count: int = typer.Option(
        0,
        '--shift-count',
        '-C',
        help="number of times to shift/lines to output before exiting; 0 means don't exit",
    )
    update_interval: float = typer.Option(
        0,
        '--update-interval',
        '-U',
        help="time in seconds to wait in between running update checking commands (i.e. the "
        "command specified by the positional argument when -u/--update-interval is specified and "
        "commands specified with -M/--match-command); 0 means check every time before printing",
    )
    eval_in_shell: bool = typer.Option(
        False,
        '--eval-in-shell',
        '-e',
        is_flag=False,
        help="whether to execute -M/--match-command and the positional argument (when "
        "-u/--update-check is true) in the shell; allows the use of environment variables "
        "(e.g. \"$PWD\"), subshells (e.g. echo \"$(/path/to/script)\"), piping, etc.; make sure "
        "to quote the commands correctly to prevent unwanted command injection",
    )

    match_command: list[str] = typer.Option(
        [],
        '--match-command',
        '-M',
        help="command(s) to search output of with --match-text",
    )
    match_text: list[tuple[str, str]] = typer.Option(
        [],
        '--match-text',
        '-m',
        # callback here will run after -M since user is required to specify -m after -M
        callback=validate_match_options,
        help="takes 2 arguments: the regexp to search for in match-command output to determine "
        "whether to change settings and the new settings themselves; see the man page for more "
        "info ",
    )


@dataclass()
class AdjustableOptions:
    """Zscroll options that can be specified locally along with --match-text."""

    length: int = typer.Option(
        40,
        '--length',
        '-l',
        callback=validate_length,
        help="length of scrolling text in number of characters excluding any before, after, and "
        "padding text and any formatting",
    )
    before_text: str = typer.Option(
        '',
        '--before-text',
        '-b',
        help="stationary padding text to display to the left of the scroll text",
    )
    after_text: str = typer.Option(
        '',
        '--after-text',
        '-a',
        help="stationary padding text to display to the right of the scroll text",
    )
    scroll_padding: str = typer.Option(
        ' - ',
        '--scroll-padding',
        '-p',
        help="padding text to display between the start and end of the scroll text only when it is "
        "scrolling",
    )
    scroll: bool = typer.Option(
        True,
        '--scroll',
        '-s',
        is_flag=False,
        help="whether to scroll; meant to be used with -m ",
    )
    update_check: bool = typer.Option(
        False,
        '--update-check',
        '-u',
        is_flag=False,
        help="specifies that the positional argument is a command that should be checked to "
        "determine if the scroll-text should be updated; when the output changes, the scroll-text "
        "is updated to the new output",
    )
    scroll_text: str = typer.Argument(
        get_stdin_if_available,
        help="text to scroll; will print in place if not longer than -l scroll length; can be read "
        "from stdin, e.g. echo text | zscroll",
        show_default=False,
    )


# TODO is there away to avoid this code duplication?
@dataclass()
class MatchAdjustableOptions:
    """Same as AdjustableOptions but each item is optional."""

    # typer can't handle int | None: https://github.com/tiangolo/typer/issues/533
    length: Optional[int] = typer.Option(  # noqa: UP007
        None,
        '--length',
        '-l',
        callback=validate_length,
        help="length of scrolling text in number of characters excluding any before, after, and "
        "padding text and any formatting",
    )
    before_text: Optional[str] = typer.Option(  # noqa: UP007
        None,
        '--before-text',
        '-b',
        help="stationary padding text to display to the left of the scroll text",
    )
    after_text: Optional[str] = typer.Option(  # noqa: UP007
        None,
        '--after-text',
        '-a',
        help="stationary padding text to display to the right of the scroll text",
    )
    scroll_padding: Optional[str] = typer.Option(  # noqa: UP007
        None,
        '--scroll-padding',
        '-p',
        help="padding text to display between the start and end of the scroll text only when it is "
        "scrolling",
    )
    update_check: Optional[bool] = typer.Option(  # noqa: UP007
        None,
        '--update-check',
        '-u',
        is_flag=False,
        help="specifies that the positional argument is a command that should be checked to "
        "determine if the scroll-text should be updated; when the output changes, the scroll-text "
        "is updated to the new output",
    )
    scroll: Optional[bool] = typer.Option(  # noqa: UP007
        None,
        '--scroll',
        '-s',
        is_flag=False,
        help="whether to scroll; meant to be used with -m ",
    )
    scroll_text: Optional[str] = typer.Argument(  # noqa: UP007
        None,
        help="text to scroll; will print in place if not longer than -l scroll length",
        show_default=False,
    )


@dataclass()
class ZscrollOptions(GlobalOptions, AdjustableOptions):
    """All zscroll command flags."""


@dataclass()
class ScrollerOptionsAndState(ZscrollOptions):
    """Zscroll commandline options and state."""

    derived_text: str | None = None
    text_index: int = 0
    shift_half_step: bool = False
    inhibit_shift: bool = False
    last_update_check_time: int | None = None
    match_index: int | None = None

    def __post_init__(self):
        """Store the default adjustable options."""
        self.default_adjustable_options = MatchAdjustableOptions(
            scroll_text=self.scroll_text,
            length=self.length,
            before_text=self.before_text,
            after_text=self.after_text,
            scroll_padding=self.scroll_padding,
            scroll=self.scroll,
        )
