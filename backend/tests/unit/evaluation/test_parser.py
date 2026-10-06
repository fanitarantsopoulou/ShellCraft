import pytest

from app.evaluation.shell.parser import ShellSyntaxError, UnsupportedSyntax, parse


def argvs(line: str) -> list[tuple[str, ...]]:
    return [c.argv for c in parse(line).commands]


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("cp a b", [("cp", "a", "b")]),
        ("  cp   a    b  ", [("cp", "a", "b")]),
        ("cp 'my file' b", [("cp", "my file", "b")]),
        ('cp "my file" b', [("cp", "my file", "b")]),
        (r"cp my\ file b", [("cp", "my file", "b")]),
        ("cp a#b c", [("cp", "a#b", "c")]),
        ("cp '$HOME' b", [("cp", "$HOME", "b")]),
        ("ls -la | grep txt", [("ls", "-la"), ("grep", "txt")]),
        ("ls|grep txt", [("ls",), ("grep", "txt")]),
    ],
)
def test_tokenizes_like_a_posix_shell(line, expected):
    assert argvs(line) == expected


def test_operators_are_recorded_in_order():
    line = parse("a && b || c ; d | e")
    assert line.operators == ("&&", "||", ";", "|")
    assert line.uses_pipe and line.uses_sequence


def test_redirects_are_separated_from_argv():
    cmd = parse("sort < in.txt > out.txt").commands[0]
    assert cmd.argv == ("sort",)
    assert cmd.redirects == (("<", "in.txt"), (">", "out.txt"))
    assert parse("echo hi >> log").uses_redirect


@pytest.mark.parametrize(
    ("line", "feature"),
    [
        ("cp $(ls) b", "expansion"),
        ("cp $HOME b", "expansion"),
        ('cp "$HOME" b', "expansion"),
        ("cp `ls` b", "expansion"),
        ("(cd /tmp)", "subshell"),
        ("sleep 1 &", "background"),
        ("ls 2> err", "fd_redirect"),
        ("ls &> all", "fd_redirect"),
        ("cp a b\nrm a", "multiline"),
    ],
)
def test_rejects_unsupported_constructs(line, feature):
    with pytest.raises(UnsupportedSyntax) as exc:
        parse(line)
    assert exc.value.feature == feature


@pytest.mark.parametrize(
    "line", ["", "   ", "cp 'a b", "| grep x", "ls |", "ls ; ; ls", "sort <", "ls >>> x"]
)
def test_rejects_invalid_shell(line):
    with pytest.raises(ShellSyntaxError):
        parse(line)
