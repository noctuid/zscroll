"""Integration tests for zscroll."""
# TODO test stdin
import pytest
from typer.testing import CliRunner

from zscroll.main import app

runner = CliRunner()


def zscroll_expect(args, expected_output):
    """Run zscroll with args and compare the output lines to the expected result."""
    # speed up run
    args = '-d 0 ' + args
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    actual_output = result.stdout.rstrip('\n').split('\n')
    # assert len(actual_output) == len(expected_output)
    assert actual_output == expected_output


def zscroll_expect_success(args):
    """Run zscroll with args and check that it exited with a zero status."""
    # speed up run
    args = '-d 0 ' + args
    result = runner.invoke(app, args)
    assert result.exit_code == 0


def zscroll_expect_error(args):
    """Run zscroll with args and check that it exited with a non-zero status."""
    # speed up run
    args = '-d 0 ' + args
    result = runner.invoke(app, args)
    assert result.exit_code != 0


# NOTE options that depend on time (--delay, --timeout, and --update-interval) are not fully tested:
# - --delay is indirectly tested; set at 0 to not slow tests
# - --timeout is only tested to check that zscroll exits
@pytest.mark.parametrize(
    ('args', 'expected_output'),
    [
        # basic fixed case
        (
            '-C 2 -p "" foobar',
            [
                'foobar',
                'foobar',
            ],
        ),
        # --shift-count longopt
        (
            '--shift-count 2 -p "" foobar',
            [
                'foobar',
                'foobar',
            ],
        ),
        # = support for longopts
        (
            '--shift-count=2 -p "" foobar',
            [
                'foobar',
                'foobar',
            ],
        ),
        # -l / basic scroll case
        (
            '-C 7 -p "" -l 5 foobar',
            [
                'fooba',
                'oobar',
                'obarf',
                'barfo',
                'arfoo',
                'rfoob',
                'fooba',
            ],
        ),
        # --length longopt
        (
            '-C 7 -p "" --length 5 foobar',
            [
                'fooba',
                'oobar',
                'obarf',
                'barfo',
                'arfoo',
                'rfoob',
                'fooba',
            ],
        ),
        # -r to reverse
        (
            '-C 7 -p "" -l 5 -r true foobar',
            [
                'fooba',
                'rfoob',
                'arfoo',
                'barfo',
                'obarf',
                'oobar',
                'fooba',
            ],
        ),
        # --reverse longopt
        (
            '-C 7 -p "" -l 5 --reverse true foobar',
            [
                'fooba',
                'rfoob',
                'arfoo',
                'barfo',
                'obarf',
                'oobar',
                'fooba',
            ],
        ),
        # -n false - test print in place
        (
            '-C 2 -p "" -n false foobar',
            ['foobar\rfoobar\r'],
        ),
        # --newline longopt
        (
            '-C 2 -p "" --newline false foobar',
            ['foobar\rfoobar\r'],
        ),
        # -u - test that text can be obtained from command
        (
            '-C 1 -p "" -u true "echo foobar"',
            [
                'foobar',
            ],
        ),
        # -u should scroll correctly (max index should be calculated from derived text not "echo
        # -foobar"; will get index error otherwise)
        (
            '-C 13 -p "" -l 5 -u true "echo foobar"',
            [
                'fooba',
                'oobar',
                'obarf',
                'barfo',
                'arfoo',
                'rfoob',
                'fooba',
                'oobar',
                'obarf',
                'barfo',
                'arfoo',
                'rfoob',
                'fooba',
            ],
        ),
        # --update-check longopt
        (
            '-C 1 -p "" --update-check true "echo foobar"',
            [
                'foobar',
            ],
        ),
        # -e false - don't evaluate in shell (default)
        (
            '-C 1 -p "" -u true "echo $(echo foobar)"',
            [
                '$(echo foobar)',
            ],
        ),
        # -e true - support subshells
        (
            '-C 1 -p "" -u true -e true "echo $(echo foobar)"',
            [
                'foobar',
            ],
        ),
        # --eval-in-shell longopt
        (
            '-C 1 -p "" -u true --eval-in-shell true "echo $(echo foobar)"',
            [
                'foobar',
            ],
        ),
        # -b - static text before scrolling text
        (
            '-C 2 -p "" -l 6 -b "b: " foobar',
            [
                'b: foo',
                'b: oob',
            ],
        ),
        # --before-text longopt
        (
            '-C 2 -p "" -l 6 --before-text "b: " foobar',
            [
                'b: foo',
                'b: oob',
            ],
        ),
        # -a - static text after scrolling text
        (
            '-C 2 -p "" -l 6 -a " :a" foobar',
            [
                'foo :a',
                'oob :a',
            ],
        ),
        # --after-text longopt
        (
            '-C 2 -p "" -l 6 --after-text " :a" foobar',
            [
                'foo :a',
                'oob :a',
            ],
        ),
        # default scroll padding
        (
            '-C 10 -l 5 foobar',
            [
                'fooba',
                'oobar',
                'obar ',
                'bar -',
                'ar - ',
                'r - f',
                ' - fo',
                '- foo',
                ' foob',
                'fooba',
            ],
        ),
        # -p - scroll padding
        (
            '-C 10 -l 5 -p " - " foobar',
            [
                'fooba',
                'oobar',
                'obar ',
                'bar -',
                'ar - ',
                'r - f',
                ' - fo',
                '- foo',
                ' foob',
                'fooba',
            ],
        ),
        # --scroll-padding longopt
        (
            '-C 10 -l 5 --scroll-padding " - " foobar',
            [
                'fooba',
                'oobar',
                'obar ',
                'bar -',
                'ar - ',
                'r - f',
                ' - fo',
                '- foo',
                ' foob',
                'fooba',
            ],
        ),
        # scroll padding in reverse
        (
            '-C 10 -l 5 -r true -p " - " foobar',
            [
                'fooba',
                ' foob',
                '- foo',
                ' - fo',
                'r - f',
                'ar - ',
                'bar -',
                'obar ',
                'oobar',
                'fooba',
            ],
        ),
        # -s false - disable scrolling
        (
            '-C 2 -p "" -l 5 -s false foobar',
            [
                'fooba',
                'fooba',
            ],
        ),
        # --scroll longopt
        (
            '-C 2 -p "" -l 5 --scroll false foobar',
            [
                'fooba',
                'fooba',
            ],
        ),
    ],
)
def test_basic_zscroll_flags(args, expected_output):
    """Test basic zscroll flags by output."""
    zscroll_expect(args, expected_output)


@pytest.mark.parametrize('args', ['-t 0.0000001 foobar', '--timeout 0.0000001 foobar'])
def test_timeout(args):
    """Test that the --timeout flag causes zscroll to exit successfully."""
    zscroll_expect_success(args)


@pytest.mark.parametrize(
    ('args', 'expected_output'),
    [
        # t
        (
            '-C 2 -p "" -l 5 -s t foobar',
            [
                'fooba',
                'oobar',
            ],
        ),
        # f
        (
            '-C 2 -p "" -l 5 -s f foobar',
            [
                'fooba',
                'fooba',
            ],
        ),
        # yes
        (
            '-C 2 -p "" -l 5 -s yes foobar',
            [
                'fooba',
                'oobar',
            ],
        ),
        # no
        (
            '-C 2 -p "" -l 5 -s no foobar',
            [
                'fooba',
                'fooba',
            ],
        ),
        # 1
        (
            '-C 2 -p "" -l 5 -s 1 foobar',
            [
                'fooba',
                'oobar',
            ],
        ),
        # 0
        (
            '-C 2 -p "" -l 5 -s 0 foobar',
            [
                'fooba',
                'fooba',
            ],
        ),
        # mixed case true
        (
            '-C 2 -p "" -l 5 -s TrUe foobar',
            [
                'fooba',
                'oobar',
            ],
        ),
        # mixed case false
        (
            '-C 2 -p "" -l 5 -s FaLsE foobar',
            [
                'fooba',
                'fooba',
            ],
        ),
    ],
)
def test_zscroll_boolean_arguments(args, expected_output):
    """Test that various strings are correctly interpreted as boolean arguments."""
    zscroll_expect(args, expected_output)


@pytest.mark.parametrize(
    ('args', 'expected_output'),
    [
        # basic case with just fullwidth, length 2
        (
            '-C 5 -p "" -l 2 あい',
            [
                'あ',
                '  ',
                'い',
                '  ',
                'あ',
            ],
        ),
        # reversed
        (
            '-C 5 -p "" -l 2 -r true あい',
            [
                'あ',
                '  ',
                'い',
                '  ',
                'あ',
            ],
        ),
        # basic case with just fullwidth, length 3
        (
            '-C 5 -p "" -l 3 あい',
            [
                'あ ',
                ' い',
                'い ',
                ' あ',
                'あ ',
            ],
        ),
        # reversed
        (
            '-C 5 -p "" -l 3 -r true あい',
            [
                'あ ',
                ' あ',
                'い ',
                ' い',
                'あ ',
            ],
        ),
        # basic length 2 mix
        (
            '-C 7 -p "" -l 2 aあ',
            [
                'a ',
                'あ',
                ' a',
                'a ',
                'あ',
                ' a',
                'a ',
            ],
        ),
        # reversed
        (
            '-C 7 -p "" -l 2 -r true aあ',
            [
                'a ',
                ' a',
                'あ',
                'a ',
                ' a',
                'あ',
                'a ',
            ],
        ),
        # more complex length 4 mix
        (
            '-C 14 -p "" -l 4 aあいiiうuえe',
            [
                'aあ ',
                'あい',
                ' いi',
                'いii',
                ' ii ',
                'iiう',
                'iうu',
                'うu ',
                ' uえ',
                'uえe',
                'えea',
                ' ea ',
                'eaあ',
                'aあ ',
            ],
        ),
        # reversed
        (
            '-C 14 -p "" -l 4 -r true aあいiiうuえe',
            [
                'aあ ',
                'eaあ',
                ' ea ',
                'えea',
                'uえe',
                ' uえ',
                'うu ',
                'iうu',
                'iiう',
                ' ii ',
                'いii',
                ' いi',
                'あい',
                'aあ ',
            ],
        ),
        # more complex length 5 mix
        (
            '-C 14 -p "" -l 5 aあいiiうuえe',
            [
                'aあい',
                'あいi',
                ' いii',
                'いii ',
                ' iiう',
                'iiうu',
                'iうu ',
                'うuえ',
                ' uえe',
                'uえea',
                'えea ',
                ' eaあ',
                'eaあ ',
                'aあい',
            ],
        ),
        # reversed
        (
            '-C 14 -p "" -l 5 -r true aあいiiうuえe',
            [
                'aあい',
                'eaあ ',
                ' eaあ',
                'えea ',
                'uえea',
                ' uえe',
                'うuえ',
                'iうu ',
                'iiうu',
                ' iiう',
                'いii ',
                ' いii',
                'あいi',
                'aあい',
            ],
        ),
        # another complex example with before, after, and padding text
        (
            '-C 15 -l 18 -b "bば: " -a " :aあ" -p "｜" aaいuえoわし',  # noqa: RUF001
            [
                'bば: aaいuえo :aあ',
                'bば: aいuえo  :aあ',
                'bば: いuえoわ :aあ',
                'bば:  uえoわ  :aあ',
                'bば: uえoわし :aあ',
                'bば: えoわし  :aあ',
                'bば:  oわし｜ :aあ',  # noqa: RUF001
                'bば: oわし｜a :aあ',  # noqa: RUF001
                'bば: わし｜aa :aあ',  # noqa: RUF001
                'bば:  し｜aa  :aあ',  # noqa: RUF001
                'bば: し｜aaい :aあ',  # noqa: RUF001
                'bば:  ｜aaいu :aあ',  # noqa: RUF001
                'bば: ｜aaいu  :aあ',  # noqa: RUF001
                'bば:  aaいuえ :aあ',
                'bば: aaいuえo :aあ',
            ],
        ),
        # reversed
        (
            '-C 15 -l 18 -b "bば: " -a " :aあ" -p "｜" -r true aaいuえoわし',  # noqa: RUF001
            [
                'bば: aaいuえo :aあ',
                'bば:  aaいuえ :aあ',
                'bば: ｜aaいu  :aあ',  # noqa: RUF001
                'bば:  ｜aaいu :aあ',  # noqa: RUF001
                'bば: し｜aaい :aあ',  # noqa: RUF001
                'bば:  し｜aa  :aあ',  # noqa: RUF001
                'bば: わし｜aa :aあ',  # noqa: RUF001
                'bば: oわし｜a :aあ',  # noqa: RUF001
                'bば:  oわし｜ :aあ',  # noqa: RUF001
                'bば: えoわし  :aあ',
                'bば: uえoわし :aあ',
                'bば:  uえoわ  :aあ',
                'bば: いuえoわ :aあ',
                'bば: aいuえo  :aあ',
                'bば: aaいuえo :aあ',
            ],
        ),
    ],
)
def test_zscroll_fixed_visual_length(args, expected_output):
    """Test that zscroll maintains a consistent "visual" length.

    Fullwidth characters should be counted as having a visual length of two and should be phased in
    and out in two steps to maintain a consistent scroll speed.
    """
    zscroll_expect(args, expected_output)


# this was originally to test a workaround for argparses completely broken behavior
# (nhttps://bugs.python.org/issue9334); now it just ensures backwards compatibility if the argument
# parsing method ever changes again
def test_zscroll_hyphen_parsing():
    """Test that arguments starting with hyphens are not automatically considered to be flags."""
    zscroll_expect(
        '-C 14 -l 13 -b "-b:" -a -a -p "--" -- "-aいuえoわし"',
        [
            '-b:-aいuえo-a',
            '-b:aいuえo -a',
            '-b:いuえoわ-a',
            '-b: uえoわ -a',
            '-b:uえoわし-a',
            '-b:えoわし--a',
            '-b: oわし---a',
            '-b:oわし----a',
            '-b:わし---a-a',
            '-b: し---a -a',
            '-b:し---aい-a',
            '-b: ---aいu-a',
            '-b:---aいu -a',
            '-b:--aいuえ-a',
        ],
    )


# TODO some way to mock a shell command to have the output change on each call (so can test
# resetting to default)
@pytest.mark.parametrize(
    ('args', 'expected_output'),
    [
        # test basic -m with -b
        (
            '-C 2 -l 6 -b "b1:" -M "echo text" -m "text" "-b b2:" foobar',
            [
                'b2:foo',
                'b2:oob',
            ],
        ),
        # test long opts
        (
            '-C 2 -l 6 -b "b1:" --match-command "echo text" '
            '--match-text "text" "--before-text b2:" foobar',
            [
                'b2:foo',
                'b2:oob',
            ],
        ),
        # test fallback when no matches
        (
            '-C 2 -l 6 -b "b1:" -M "echo nomatch" -m "text" "-b b2:" foobar',
            [
                'b1:foo',
                'b1:oob',
            ],
        ),
        # test -m with -a
        (
            '-C 2 -l 6 -a ":a1" -M "echo text" -m "text" "-a :a2" foobar',
            [
                'foo:a2',
                'oob:a2',
            ],
        ),
        # test -m with -p
        (
            '-C 5 -l 2 -M "echo text" -m "text" "-p %" foo',
            [
                'fo',
                'oo',
                'o%',
                '%f',
                'fo',
            ],
        ),
        # test -m with -s
        (
            '-C 2 -l 2 -M "echo text" -m "text" "-s false" foo',
            [
                'fo',
                'fo',
            ],
        ),
        # test -m with -l
        (
            '-C 2 -l 100 -M "echo text" -m "text" "-l 5" foobar',
            [
                'fooba',
                'oobar',
            ],
        ),
        # test -m with new scroll text/positional argument
        (
            '-C 2 -l 5 -M "echo text" -m "text" "bazqux" foobar',
            [
                'bazqu',
                'azqux',
            ],
        ),
        # test using .* regexp to check for command success
        (
            '-C 2 -l 2 -M "true" -m ".*" "-s false" foo',
            [
                'fo',
                'fo',
            ],
        ),
        # test -m with -u; change in -u should be immediately detected
        (
            '-C 14 -l 10 -b "b: " -a " :a" -p "|" -M "echo text"'
            ' -m "text" "-u t -b > -a < -p \' | \' \'echo aaいuえoわし\'" "failed"',
            [
                '>aaいuえo<',
                '>aいuえo <',
                '>いuえoわ<',
                '> uえoわ <',
                '>uえoわし<',
                '>えoわし <',
                '> oわし |<',
                '>oわし | <',
                '>わし | a<',
                '> し | aa<',
                '>し | aa <',
                '>  | aaい<',
                '> | aaいu<',
                '>| aaいu <',
            ],
        ),
        # test mix of long and short options
        (
            '-C 14 -l 10 -b "b: " --after-text " :a" --scroll-padding "|" -M "echo text"'
            ' -m "text" "--update-check t --before-text > -a < -p \' | \' \'echo aaいuえoわし\'"'
            ' "failed"',
            [
                '>aaいuえo<',
                '>aいuえo <',
                '>いuえoわ<',
                '> uえoわ <',
                '>uえoわし<',
                '>えoわし <',
                '> oわし |<',
                '>oわし | <',
                '>わし | a<',
                '> し | aa<',
                '>し | aa <',
                '>  | aaい<',
                '> | aaいu<',
                '>| aaいu <',
            ],
        ),
        # test 1 -M and multiple -m; test that last -m has precedence
        (
            '-C 14 -l 10 -b "b: " -a " :a" -p "|" -d 0.0000001 -M "echo txt"'
            ' -m "txt" "-s no \'echo abcdefghijk\'" -M "echo text"'
            ' -m "text" "-u t -b > -a < -p \' | \' \'echo aaいuえoわし\'" "failed"',
            [
                '>aaいuえo<',
                '>aいuえo <',
                '>いuえoわ<',
                '> uえoわ <',
                '>uえoわし<',
                '>えoわし <',
                '> oわし |<',
                '>oわし | <',
                '>わし | a<',
                '> し | aa<',
                '>し | aa <',
                '>  | aaい<',
                '> | aaいu<',
                '>| aaいu <',
            ],
        ),
        # test multiple -M and -m
        (
            '-C 14 -l 10 -b "b: " -a " :a" -p "|" -d 0.0000001 -M "echo text"'
            ' -m "text" "-u t -b > -a < -p \' | \' \'echo aaいuえoわし\'" "failed"'
            ' -m "txt" "-s no \'echo abcdefghijk\'" -M "echo text"',
            [
                '>aaいuえo<',
                '>aいuえo <',
                '>いuえoわ<',
                '> uえoわ <',
                '>uえoわし<',
                '>えoわし <',
                '> oわし |<',
                '>oわし | <',
                '>わし | a<',
                '> し | aa<',
                '>し | aa <',
                '>  | aaい<',
                '> | aaいu<',
                '>| aaいu <',
            ],
        ),
    ],
)
def test_zscroll_match_command(args, expected_output):
    """Test zscroll's --match-command and --match-text flags."""
    zscroll_expect(args, expected_output)


@pytest.mark.parametrize(
    'args',
    [
        # non-number
        '-C two',
        # invalid boolean
        '-C 2 -s any foobar',
        # negative length
        '-C 2 -l -1 foobar',
        # test -m with unsupported option (-n false should be ignored)
        # TODO will print error but not exit; should it exit if parsing fails?
        # '-C 2 -M "echo text" -m "text" "-n false" foobar',
        # -m and -M count mismatch
        '-C 2 -M "echo 1" -m "1" "-l 1" -M "echo 2" -m "2" "-l 2" -m "text3" "-l 3"',
    ],
)
def test_zscroll_validation(args):
    """Test that zscroll's validation fails invalid options/arguments."""
    zscroll_expect_error(args)
