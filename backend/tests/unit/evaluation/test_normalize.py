from hypothesis import given
from hypothesis import strategies as st

from app.evaluation.context import EvalContext
from app.evaluation.shell.normalize import canonicalize
from app.evaluation.shell.parser import parse
from tests.factories import cp_command

CTX = EvalContext(commands={"cp": cp_command()})


def canon(line: str, **kw):
    return canonicalize(parse(line), CTX, **kw)


def test_bundled_short_flags_equal_separate_flags():
    assert canon("cp -rv a b") == canon("cp -r -v a b")


def test_all_spellings_of_an_option_are_equivalent():
    assert canon("cp -r a b") == canon("cp -R a b") == canon("cp --recursive a b")


def test_options_may_follow_operands():
    assert canon("cp a b -v") == canon("cp -v a b")


def test_double_dash_ends_options():
    assert canon("cp -- a b") == canon("cp a b")
    assert canon("cp -- -v b").commands[0].operands == ("-v", "b")


def test_operand_order_matters():
    assert canon("cp a b") != canon("cp b a")


def test_option_values_are_path_normalized():
    assert canon("cp -t ./dir a") == canon("cp -t dir a")


def test_required_values_attached_or_separate():
    assert canon("cp -t dir a") == canon("cp -tdir a") == canon("cp --target-directory=dir a")
    assert canon("cp --target-directory dir a") == canon("cp -t dir a")
    assert canon("cp -t dir a") != canon("cp -t a dir")


def test_missing_and_unknown_options_are_reported():
    assert canon("cp a -t").commands[0].missing_values == ("-t",)
    assert canon("cp -z a b").commands[0].unknown_options == ("-z",)
    assert canon("cp --recursive=yes a b").commands[0].unknown_options == ("--recursive=yes",)


def test_optional_value_only_with_equals():
    c = canon("cp --backup=numbered a b").commands[0]
    assert ("--backup", "numbered") in c.options


def test_dot_slash_normalization_is_configurable():
    assert canon("cp ./a b") == canon("cp a b")
    assert canon("cp ./a b", strip_dot_slash=False) != canon("cp a b", strip_dot_slash=False)
    assert canon("cp ./ b").commands[0].operands == ("./", "b")


def test_unknown_commands_compare_literally():
    assert canon("foo -ab x") != canon("foo -a -b x")
    assert canon("foo -a x") == canon("foo -a x")
    assert canon("foo -a ./x") == canon("foo -a x")


def test_optional_flags_are_ignored_on_both_sides():
    opt = {"cp": ["-i", "--verbose"]}
    assert canon("cp -iv a b", optional_flags=opt) == canon("cp a b", optional_flags=opt)
    assert canon("cp -r a b", optional_flags=opt) != canon("cp a b", optional_flags=opt)


FLAGS = ["-r", "-i", "-v", "-s"]


@given(st.permutations(FLAGS), st.integers(min_value=0, max_value=2))
def test_flag_permutation_and_position_do_not_matter(perm, position):
    operands = ["src", "dst"]
    tokens = operands[:position] + list(perm) + operands[position:]
    assert canon("cp " + " ".join(tokens)) == canon("cp -r -i -v -s src dst")


@given(st.text(alphabet="abcxyz._/-", min_size=1, max_size=12))
def test_canonicalization_is_deterministic(name):
    line = f"cp -- '{name}' dest"
    assert canon(line) == canon(line)


def test_numeric_shorthand():
    head = cp_command(
        id="head",
        name="head",
        numeric_shorthand="-n",
        options=[{"flags": ["-n", "--lines"], "summary": "lines", "value": "required"}],
        related=[],
    )
    ctx = EvalContext(commands={"head": head})

    def c(line):
        return canonicalize(parse(line), ctx)

    assert c("head -5 f") == c("head -n 5 f") == c("head --lines=5 f") == c("head -n5 f")
    assert c("head -5 f").commands[0].shorthands == (("-5", "-n 5"),)
    assert c("head -n 5 f").commands[0].shorthands == ()
    assert c("head -5 f") != c("head -n 6 f")


def docker_run():
    return cp_command(
        id="docker-container-run",
        name="docker container run",
        aliases=["docker run"],
        flag_grammar="pflag",
        interspersed=False,
        options=[
            {"flags": ["-d", "--detach"], "summary": "detach"},
            {"flags": ["-i", "--interactive"], "summary": "stdin"},
            {"flags": ["-t", "--tty"], "summary": "tty"},
            {"flags": ["-p", "--publish"], "summary": "publish", "value": "required"},
            {"flags": ["--name"], "summary": "name", "value": "required"},
        ],
        related=[],
    )


DCTX = EvalContext(commands={"docker-container-run": docker_run()})


def dcanon(line):
    return canonicalize(parse(line), DCTX)


def test_alias_maps_to_command_name():
    assert dcanon("docker run nginx") == dcanon("docker container run nginx")
    assert dcanon("docker run nginx").commands[0].name == "docker container run"


def test_pflag_options_are_order_insensitive_and_accept_equals():
    expected = dcanon("docker run -d -p 8080:80 --name web nginx")
    assert dcanon("docker run --name=web -p8080:80 -d nginx") == expected
    assert dcanon("docker container run -p=8080:80 --detach --name web nginx") == expected


def test_non_interspersed_options_after_image_belong_to_the_container():
    # `-d` after the image is an argument to the container, not docker's --detach.
    assert dcanon("docker run nginx -d") != dcanon("docker run -d nginx")
    assert dcanon("docker run nginx -d").commands[0].operands == ("nginx", "-d")
    assert dcanon("docker run -it ubuntu bash") == dcanon("docker run -i -t ubuntu bash")


def test_unknown_subcommand_is_literal():
    c = dcanon("docker frobnicate -x").commands[0]
    assert c.name == "docker" and c.operands == ("frobnicate", "-x")
