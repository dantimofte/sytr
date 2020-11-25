import pytest
from sytr.tools import cli
from argparse import Namespace
from io import TextIOWrapper
import requests_mock


@pytest.fixture(scope="session")
def input_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("file.txt")
    fn.write("some content to be translated")
    return fn


def test_default_url_exist():
    assert cli.URL == "http://localhost:5000/api/translate"


def test_get_arguments(input_file):
    args = cli.get_arguments(["-f", str(input_file), "-l", "en"])
    assert isinstance(args, Namespace)
    assert isinstance(args.f, TextIOWrapper)
    assert args.f.name == str(input_file)
    assert args.l == "en"


@pytest.mark.parametrize("input_args", [
    (["-f", "file2.txt", "-l", "en"],),
    (["-f", "file2.txt", "-l"],),
])
def test_bad_arguments(input_args):
    with pytest.raises(SystemExit):
        cli.get_arguments(input_args)


def test_get_lines_from_file(input_file):
    with open(input_file) as file:
        resp = cli.get_lines_from_file(file)
    assert resp == tuple(("some content to be translated",))


def test_translate_text():
    request_result = {'ok': True, 'translations': ['Good morning', 'Good day']}
    adapter = requests_mock.Adapter()
    cli.REQUEST_SESSION.mount('mock://test.com/api/translate', adapter)
    adapter.register_uri(
        'POST',
        'mock://test.com/api/translate',
        text='{"ok": true, "translations": ["Good morning", "Good day"]}'
    )
    cli.URL = 'mock://test.com/api/translate'
    response = cli.translate_text(["Buna Dimineata", "Gutten tag"], "en")
    assert response == request_result


def test_print_response(capsys):
    cli.print_response({'ok': True, 'translations': ["Good morning", "Good day"]})
    captured = capsys.readouterr()
    assert captured.out == "Good morning\nGood day\n"
