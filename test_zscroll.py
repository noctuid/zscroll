"""Tests for zscroll."""
import os
import sys
from imp import load_source
from shlex import split

import pytest

z = load_source('zscroll', './zscroll')


@pytest.mark.parametrize(
    'string,expected_length', [
        ('foo bar', 7),
        ('ふば', 4),
        ('ふbar', 5),
    ]
)
def test_visual_len(string, expected_length):
    assert z.visual_len(string) == expected_length


@pytest.mark.parametrize(
    'string,new_length,new_string', [
        ('foo bar', 5, 'foo b'),
        ('foo', 5, 'foo  '),
        ('ふば', 3, 'ふ '),
        ('ふば', 2, 'ふ'),
    ]
)
def test_make_visual_len(string, new_length, new_string):
    assert z.make_visual_len(new_length, string) == new_string


@pytest.mark.parametrize('command,result', [
    ('echo test', 'test'),
    ('false', ''),
])
def test_shell_output(command, result):
    assert z.shell_output(command) == result


@pytest.mark.parametrize('arg_string,result', [
    # basic case with both fullwidth and halfwidth characters
    ('-l 8 -b "b: " -a " :a" -p "|" -d 0.0000001 "aaいuえoわし"',
     ['b: aaいuえo :a',
      'b: aいuえo  :a',
      'b: いuえoわ :a',
      'b:  uえoわ  :a',
      'b: uえoわし :a',
      'b: えoわし| :a',
      'b:  oわし|a :a',
      'b: oわし|aa :a',
      'b: わし|aa  :a',
      'b:  し|aaい :a',
      'b: し|aaいu :a',
      'b:  |aaいu  :a',
      'b: |aaいuえ :a',
      'b: aaいuえo :a', ]),
    # test --reverse
    ('-r true -l 8 -b "b: " -a " :a" -p "|" -d 0.0000001 "aaいuえoわし"',
     ['b: aaいuえo :a',
      'b: |aaいuえ :a',
      'b:  |aaいu  :a',
      'b: し|aaいu :a',
      'b:  し|aaい :a',
      'b: わし|aa  :a',
      'b: oわし|aa :a',
      'b:  oわし|a :a',
      'b: えoわし| :a',
      'b: uえoわし :a',
      'b:  uえoわ  :a',
      'b: いuえoわ :a',
      'b: aいuえo  :a',
      'b: aaいuえo :a', ]),
    # test --update-check
    ('-l 8 -b "b: " -a " :a" -p "|" -d 0.0000001 -u true "echo aaいuえoわし"',
     ['b: aaいuえo :a',
      'b: aいuえo  :a',
      'b: いuえoわ :a',
      'b:  uえoわ  :a',
      'b: uえoわし :a',
      'b: えoわし| :a',
      'b:  oわし|a :a',
      'b: oわし|aa :a',
      'b: わし|aa  :a',
      'b:  し|aaい :a',
      'b: し|aaいu :a',
      'b:  |aaいu  :a',
      'b: |aaいuえ :a',
      'b: aaいuえo :a', ]),
    # test arguments that start with -
    ('-l 8 -b "-b:" -a "-a" -p "--" -d 0.0000001 -- "-aいuえoわし"',
     ['-b:-aいuえo-a',
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
      '-b:--aいuえ-a', ]),
    # test -m (and that change in -u will be immediately detected)
    ('-l 8 -b "b: " -a " :a" -p "|" -d 0.0000001 -M "echo text"' + \
     ' -m "text" "-u t -b > -a < -p \' | \' \'echo aaいuえoわし\'" "failed"',
     ['>aaいuえo<',
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
      '>| aaいu <', ]),
    # last -m should take precedence
    ('-l 8 -b "b: " -a " :a" -p "|" -d 0.0000001 -M "echo txt"' + \
     ' -m "txt" "-s no \'echo abcdefghijk\'" -M "echo text"' + \
     ' -m "text" "-u t -b > -a < -p \' | \' \'echo aaいuえoわし\'" "failed"',
     ['>aaいuえo<',
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
      '>| aaいu <', ]),
])
def test_zscroll(arg_string, result, capfd):
    # reload default settings
    z = load_source('zscroll', './zscroll')
    argv = ['zscroll'] + split(arg_string)
    argv = z.pre_parse_argv(argv)
    z.parse_argv(argv)
    z.zscroll(14)
    out, err = capfd.readouterr()
    out = out.rstrip().split('\n')
    assert out == result


@pytest.mark.parametrize('arg_string', [
    # no scroll-text specified
    ('-n true'),
    # no -M specified with -m
    ('-m match-text "-s no" scroll-text'),
    # number of -M > 1 but does not match number of -m
    ('-M command1 -m text1 \'-s f\' -M command2 -m text2 \'-s f\'' + \
     ' -m text3 \'-s f\' scroll-text'),
])
def test_validate_args(arg_string):
    # reload default settings
    z = load_source('zscroll', './zscroll')
    argv = ['zscroll'] + split(arg_string)
    argv = z.pre_parse_argv(argv)
    z.parse_argv(argv)
    with pytest.raises(SystemExit):
        # silence help text
        old_stdout = sys.stdout
        null = open(os.devnull, 'w')
        sys.stdout = null
        z.validate_args(z.args)
        sys.stdout = old_stdout
