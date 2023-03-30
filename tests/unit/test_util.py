"""Unit tests for zscroll's util.py."""
import pytest

from zscroll.util import shell_output, visual_len, visual_slice


# TODO maybe use something like pytest-spec (e.g. describe visual_len, "It reports the character
# count for strings composed of only halfwidth characters"); couldn't get pytest-spec working
# - doesn't support nesting - https://github.com/gwthm-in/pytest-pspec
# - also https://nestorsalceda.com/mamba/


@pytest.mark.parametrize(
    ('string', 'expected_length'),
    [
        ('', 0),
        # halfwidth only strings
        ('foo', 3),
        ('foo bar', 7),
        # fullwidth only strings
        ('ふ', 2),
        ('ふば', 4),
        # mix
        ('ふbar', 5),
        ('ふ bar バズ', 11),
    ],
)
def test_visual_len(string, expected_length):
    """Test zscroll's visual_len function."""
    assert visual_len(string) == expected_length


@pytest.mark.parametrize(
    ('command', 'expected_result'),
    [
        ('echo test', 'test'),
        # should return None if errors (nothing will match)
        ('false', None),
    ],
)
def test_shell_output(command, expected_result):
    """Test zscroll's shell_output function."""
    assert shell_output(command) == expected_result


@pytest.mark.parametrize(
    ('command', 'expected_result'), [('echo $(echo test)', 'test'), ('false', None)]
)
def test_eval_shell_output(command, expected_result):
    """Test zscroll's shell_output function with evaluation in shell."""
    assert shell_output(command, True) == expected_result


@pytest.mark.parametrize(
    ('text', 'index', 'length', 'expected_result'),
    [
        # starting at index 0
        # 0 length
        ('foo bar', 0, 0, ''),
        ('foo bar', 0, -1, ''),
        # basic
        ('foo bar', 0, 5, 'foo b'),
        # adds padding
        ('foo', 0, 5, 'foo  '),
        # handles full width
        ('ふば', 0, 1, ' '),
        ('ふば', 0, 2, 'ふ'),
        ('ふば', 0, 3, 'ふ '),
        ('ふば', 0, 4, 'ふば'),
        # handles index
        ('ふば', 1, 2, 'ば'),
        ('ふば', 1, 3, 'ば '),
        # handles wrapping
        ('ふば', 1, 4, 'ばふ'),
        ('ふば', 2, 4, 'ふば'),
        # negative start index
        ('ふば', -1, 4, 'ばふ'),
        ('ふば', -2, 4, 'ふば'),
    ],
)
def test_visual_slice(text, index, length, expected_result):
    """Test zscroll's visual_slice function."""
    assert visual_slice(text, index, length) == expected_result
