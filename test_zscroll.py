"""Tests for zscroll."""
import pytest
from shlex import split
from imp import load_source
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
])
def test_shell_output(command, result):
    assert z.shell_output(command) == result


@pytest.mark.parametrize('arg_list,result', [
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
     ' -m "text" "-b > -a < -p \' | \' \'echo aaいuえoわし\'" "aaいuえoわし"',
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
    ('-l 8 -b "b: " -a " :a" -p "|" -d 0.0000001 -M "echo text"' + \
     ' -m "txt" "-b b -a a -p \' - \' \'echo abcdefghijk\'"' + \
     ' -m "text" "-b > -a < -p \' | \' \'echo aaいuえoわし\'" "aaいuえoわし"',
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
def test_zscroll(arg_list, result, capfd):
    # reload default settings
    z = load_source('zscroll', './zscroll')
    argv = ['zscroll'] + split(arg_list)
    argv = z.pre_parse_argv(argv)
    z.parse_argv(argv)
    z.zscroll(14)
    out, err = capfd.readouterr()
    out = out.rstrip().split('\n')
    assert out == result
