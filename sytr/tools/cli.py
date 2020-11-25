import os
import sys
import argparse
import requests

VERSION = 1.0
HOST = os.environ.get("host", "http://localhost:5000")
URL = f"{HOST}/api/translate"
REQUEST_SESSION = requests.Session()


def get_arguments(args):
    """
    Function responsible for parsing the command line arguments
    For the first argument it will try and open the file specified
    For the second argument it will only accept one of the 3 target languages allowed
    :return:
    """
    parser = argparse.ArgumentParser(description=f'gtranslate {VERSION}: command line utility for translating text')
    parser.add_argument(
        '-f',
        type=argparse.FileType('r', encoding='UTF-8'),
        required=True,
        metavar='<filename>',
        help='path to input filename to be translated'
    )
    parser.add_argument(
        '-l',
        type=str,
        metavar='<lang>',
        choices=['en', 'it', 'de'],
        help='output language, can be one of "en", "it" or "de"'
    )
    return parser.parse_args(args)


def get_lines_from_file(file):
    """
    Function that creates a tuple with the lines from the files
    it strip any blank character from the right side
    it removes empty lines
    :param file:
    :return: tuple of strings
    """
    lines_to_translate = tuple(line.rstrip() for line in file.readlines() if line.strip())
    return lines_to_translate


def translate_text(lines_to_translate, target_language):
    data = {
        "text": lines_to_translate,
        "target_language": target_language
    }
    req_response = None
    try:
        req_response = REQUEST_SESSION.post(URL, json=data)
    except requests.exceptions.ConnectionError:
        print("Error: Connection to translating daemon failed")
        exit(1)
    if req_response.status_code != 200:
        print(f"Error: Backend returned {req_response.status_code} {req_response.reason}")
        exit(1)

    return req_response.json()


def print_response(translate_data):
    if translate_data.get("ok"):
        for line in translate_data.get("translations"):
            print(line)
    else:
        print(f"Backend returned these error codes : {' '.join(translate_data.get('errors'))}")


def main():
    args = get_arguments(sys.argv[1:])
    lines_to_translate = get_lines_from_file(args.f)
    args.f.close()
    if not lines_to_translate:
        exit(f"Nothing to translate in the file {args.f.name}")

    print("Translating, please wait...")
    translate_data = translate_text(lines_to_translate, args.l)
    print_response(translate_data)


if __name__ == "__main__":
    main()
