import json
import os
import requests
import sys
import time
sys.path.insert(0, '/Users/srosenberg/go/src/github.com/Saraislet/pybuildkite')
from pybuildkite.buildkite import Buildkite, BuildState

# Requires Python 3.6+ (because fstrings <3)
#
# Run with this command:
# python3 run_build_task.py build_task.json
#
# Create a Buildkite API token here:
# https://buildkite.com/user/api-access-tokens
if not os.environ.get('BUILDKITE_TOKEN'):
    print('Please load Buildkite API token into environment variable BUILDKITE_TOKEN.\n\n'
          + 'Create Buildkite API token here: '
          + 'https://buildkite.com/user/api-access-tokens\n'
          + 'Scope: read_builds, write_builds, read_build_logs')
    exit(1)

TOKEN = os.environ['BUILDKITE_TOKEN']
HEADERS = {'Authorization': 'Bearer '+TOKEN}
ORG = 'pagerduty'
API_BASE_URL = 'https://api.buildkite.com/v2/organizations/' + ORG + '/'
unblock_filename = 'unblock_fields.json'

bk = Buildkite()
bk.set_access_token(TOKEN)

if len(sys.argv) < 2:
    job_filename = input('Please enter job json filename: ')
else:
    job_filename = sys.argv[1]


def load_json(filename):
    data = {}
    with open(filename) as file:
        data = json.load(file)
    return data


def run_build(job_filename):
    build_task = load_json(job_filename)

    build = start_build(build_task)
    build_details = get_build(build)
    build_result = unblock_build(build_details)


def start_build(build_task):
    message = build_task['message'] or None

    return bk.builds().create_build(organization=ORG,
                                 pipeline=build_task['pipeline'],
                                 commit=build_task['commit'],
                                 branch=build_task['branch'],
                                 message=build_task['message'],
                                 ignore_pipeline_branch_filters=True)


def get_build(build):
    return bk.builds().get_build_by_number(organization=ORG,
                                           pipeline=build['pipeline']['slug'],
                                           build_number=build['number'])


def get_build_number(build_task, build_number):
    return bk.builds().get_build_by_number(organization=ORG,
                                           pipeline=build_task['pipeline'],
                                           build_number=build_number)


def get_unblock_fields(build_task):
    unblock_fields = load_json(unblock_filename)
    fields = unblock_fields.get(build_task['pipeline'])
    if not fields:
        raise KeyError

    fields = fields[0]
    for key, value in fields.items():
        if not value:
            if build_task.get('unblock_fields') and build_task['unblock_fields'].get(key):
                fields[key] = build_task['unblock_fields'][key]
            else:
                fields[key] = input('Please enter unblock value for ' + key + ': ')

    return fields



def unblock_build(build):
    build = get_build(build)
    for i, job in enumerate(build['jobs']):
        state_printed = None
        while job.get('state') != 'passed' and job.get('state') != 'unblocked':
            if job.get('type') == 'waiter':
                break

            if not state_printed:
                state_printed = str(job.get('state'))
                print('\nLabel: ' + str(job.get('label'))
                      + '\nState: ' + state_printed)

            if job.get('state') == 'blocked' and job.get('type') == 'manual':
                print('\nAttempting to unblock')
                fields = get_unblock_fields(build_task)
                r = bk.jobs().unblock_job(organization=ORG,
                                          pipeline=build['pipeline']['slug'],
                                          build=build['number'],
                                          job=job['id'],
                                          fields=fields)
                if r.get('state') and r['state'] == 'unblocked':
                    print("Step unblocked\n")
                    break

            time.sleep(3)
            build = get_build(build)
            job = build['jobs'][i]
if __name__ == '__main__':
    print(f"Loading job details from file '{job_filename}'")
    build_task = load_json(job_filename)
    run_build(job_filename)
