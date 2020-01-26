import run_build_task

from getpass import getpass
import os
import sys

# Requires Python 3.6+ (because fstrings <3)
#
# Create a Buildkite API token here:
# https://buildkite.com/user/api-access-tokens

JSON_PATH = '.'


def get_token():
    TOKEN = os.environ.get('BUILDKITE_TOKEN')
    if not TOKEN:
        TOKEN = getpass('Please enter your Buildkite API token.\n'
                         + 'The token should have scopes read_builds, '
                         + 'write_builds, read_pipelines.\n'
                         + 'https://buildkite.com/user/api-access-tokens\n> ')
    if not TOKEN:
        print('Missing token.')
        exit(1)
    return TOKEN


def get_json_filenames(path):
    return [f for f in os.listdir(path) if f.endswith(".json")]


def pick_file(filenames):
    # Don't make me write pagination.
    # Fuck it, fine.
    offset = 0
    count = 10
    print("\nPlease select a file.\n")
    while True and offset < len(filenames):
        for i, f in enumerate(filenames[offset:offset+count]):
            print(f"({i}) {f}\n")
        print("(m) more\n\n")

        choice = input("> ")
        if choice in range(offset, count):
            return filenames(choice)

        if choice.lower() == 'm':
            offset += count
            continue

        # passive-aggressively end program
        print("I'm sorry, I didn't understand your input.")
        exit(1)


if __name__ == '__main__':
    TOKEN = get_token()
    json_filenames = get_json_filenames(JSON_PATH)
    filename = pick_file(json_filenames)
    build_task = run_build_task.load_json(filename)    

