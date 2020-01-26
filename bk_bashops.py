import run_build_task

from getpass import getpass
from pprint import pprint
import os
import sys

# Requires Python 3.6+ (because fstrings <3)
#
# Create a Buildkite API token here:
# https://buildkite.com/user/api-access-tokens

JSON_PATH = '.'


def get_json_filenames(path):
    return [f for f in os.listdir(path) if f.endswith(".json")]


def pick_file(filenames):
    # Don't make me write pagination.
    # Okay, fine.
    offset = 0
    count = 10
    print("\nPlease select a file.\n")
    while True and offset < len(filenames):
        for i, f in enumerate(filenames[offset:offset+count]):
            print(f"({i}) {f}")
        print("(m) more\n")

        choice = input("> ")
        print('\n', end='')
        if choice.lower() == 'm':
            offset += count
            continue

        if choice.isnumeric() and int(choice) in range(offset, count):
            return filenames[int(choice)]

        # passive-aggressively end program
        print("I'm sorry, I didn't understand your input.")
        exit(1)


def run_tasks(task_queue):
    for task in task_queue:
        print(f"\n Starting task: {task[0]}")
        build_tasks = run_build_task.load_json(task[0])
        build_task = build_tasks[task[1]]
        pprint(build_task)
        run_build_task.run_build(build_task)
    print('Finished with all tasks in the queue.')


def handle_tasks(task_queue):
    json_filenames = get_json_filenames(JSON_PATH)
    while True:
        task_queue.append((pick_file(json_filenames), 0))
        print(task_queue)
        print('Would you like to add another task to the queue?')
        choice = input('y/n > ')
        if choice.lower() != 'y':
            break
    run_tasks(task_queue)


if __name__ == '__main__':
    task_queue = []
    handle_tasks(task_queue)
