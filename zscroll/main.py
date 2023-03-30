"""A text scroller for panels or terminals."""
import re
import shlex
import sys
from contextlib import suppress
from dataclasses import asdict
from time import sleep, time

import typer

from zscroll.models import (
    MatchAdjustableOptions,
    ScrollerOptionsAndState,
    ZscrollOptions,
)
from zscroll.util import inject_dataclass_args, shell_output, visual_len, visual_slice

app = typer.Typer()

# * Scroller
class Scroller(ScrollerOptionsAndState):
    """Scroller responsible for continuously printing shifting text."""

    def reset_scroll(self):
        """Reset scrolling (e.g. after the text to print changes)."""
        self.text_index = 0
        # TODO reset direction if bounce

    def update_scroll_text_check(self) -> bool:
        """Update the scroll-text if the command output has changed.

        If the update check option is False, do nothing and return False.

        If the scroll-text changes, reset the scroll position/information.

        :return: whether the scroll-text has changed
        """
        if not self.update_check:
            return False

        output = shell_output(self.scroll_text, self.eval_in_shell)

        if self.derived_text != output:
            self.derived_text = output
            self.reset_scroll()
            return True
        return False

    def _update_match_options(self, new_opts: MatchAdjustableOptions):
        if new_opts.length is not None:
            self.length = new_opts.length
        if new_opts.before_text is not None:
            self.before_text = new_opts.before_text
        if new_opts.after_text is not None:
            self.after_text = new_opts.after_text
        if new_opts.scroll_padding is not None:
            self.scroll_padding = new_opts.scroll_padding
        if new_opts.scroll is not None:
            self.scroll = new_opts.scroll
        if new_opts.update_check is not None:
            self.update_check = new_opts.update_check
        if new_opts.scroll_text is not None:
            self.scroll_text = new_opts.scroll_text

    def update_match_options(self):
        """Update settings/state based on the current match.

        If there is no match, reset to the default settings.
        """
        if self.match_index is not None and self.match_index < len(self.match_text):
            matched_options = self.match_text[self.match_index][1]
            # HACK setting sys.arv and then running another typer command because typer has no way
            # to manually parse arguments
            sys.argv = sys.argv[0:1] + shlex.split(matched_options)

            @inject_dataclass_args(MatchAdjustableOptions)
            def _update_opts(new_opts: MatchAdjustableOptions):
                self._update_match_options(new_opts)

            subapp = typer.Typer(add_completion=False)
            subapp.command()(_update_opts)
            # prevent exiting after printing finishes
            with suppress(SystemExit):
                subapp()
        else:
            # reset to the default settings
            self._update_match_options(self.default_adjustable_options)

    def update_options_check(self):
        """Check match-command(s) for match-text and update formatting options if necessary.

        When there are match commands to check, run each command and search for the corresponding
        match/search text.  Store the last match's (if any) index and retrieve/use the
        associated settings.  If there are no matches or no match commands to check, set the matched
        index to None and retrieve/use the default settings instead.

        If the match index changes, reset the scroll position/information.
        """
        if len(self.match_command) == 0:
            return

        match_found = False
        previous_index = self.match_index
        for i, match_text in enumerate(self.match_text):
            search_text = shell_output(self.match_command[i], self.eval_in_shell)
            if search_text is not None and re.search(match_text[0], search_text):
                match_found = True
                self.match_index = i
        if not match_found:
            self.match_index = None
        if self.match_index != previous_index:
            # needed when shifting, not just when printing
            self.update_match_options()
            self.reset_scroll()

    def maybe_update_text_and_options(self):
        """Update the scroll-text and/or formatting options if necessary.

        If the update interval option is set, update after that time interval has passed rather
        than on each call.
        """
        if (
            self.update_interval == 0
            or self.last_update_check_time is None
            or self.last_update_check_time + self.update_interval < time()
        ):
            # must come before updating scroll text since it can change the scroll text command
            self.update_options_check()
            self.update_scroll_text_check()
            self.last_update_check_time = time()

    def shift(self):
        """Increment the index to start printing the text.

        If --reverse true was specified, decrement the index instead.
        """
        if self.inhibit_shift:
            self.inhibit_shift = False
            return
        text = self.derived_text or self.scroll_text
        # not merging yet but need to include padding text when calculating index to not skip over
        # the padding
        max_index = len(text + self.scroll_padding) - 1
        # TODO add bounce (self.increment)
        if self.reverse:
            self.text_index -= 1
            if self.text_index < 0:
                self.text_index = max_index
        else:
            self.text_index += 1
            if self.text_index > max_index:
                self.text_index = 0

    # TODO don't repeatedly mutate variables for clarity?
    def print_text(self):
        """Build and print the current text.

        Ensure the text always matches the user-specified "visual" length and phase fullwidth
        characters out (and in) in two steps by replacing them with a space before moving onto the
        next character.
        """
        text = self.derived_text or self.scroll_text
        before_text = self.before_text
        if visual_len(self.before_text + text + self.after_text) > self.length:
            remaining_length = max(
                0, self.length - visual_len(self.before_text) - visual_len(self.after_text)
            )
            if self.scroll:
                index = self.text_index
                text += self.scroll_padding
                # TODO this could probably be simplified
                # for phasing out fullwidth characters
                if self.shift_half_step:
                    before_text += ' '
                    remaining_length -= 1
                    self.shift_half_step = False
                    # keep index at current character
                    self.inhibit_shift = True
                    # print space before fullwidth character when scrolling in reverse
                    if self.reverse:
                        index += 1
                elif visual_len(text[index - 1 if self.reverse else index]) == 2:
                    self.shift_half_step = True

                text = visual_slice(text, index, remaining_length)
            else:
                text = visual_slice(text, 0, remaining_length)
        text = before_text + text + self.after_text
        end = '\n' if self.newline else '\r'
        print(text, end=end, flush=True)  # noqa: T201

    def loop(self):
        """Continuously shift and print text until reaching a timeout or maximum scroll count.

        On each iteration check if the scroll text or local settings should be updated (based on
        --update-check and --match-command/--match-text).
        """
        end_time = time() + self.timeout
        shift_count = 0
        while True:
            if (self.timeout and time() > end_time) or (
                self.max_shift_count > 0 and shift_count == self.max_shift_count
            ):
                break
            shift_count += 1
            self.maybe_update_text_and_options()
            self.print_text()
            self.shift()
            sleep(self.delay)


# * Main
@app.command()
@inject_dataclass_args(ZscrollOptions)
def main(opts: ZscrollOptions):
    """Print scrolling text until interrupted."""
    try:
        Scroller(**asdict(opts)).loop()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    app()
