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
# python3 run_job.py job.json
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

bk = Buildkite()
bk.set_access_token(TOKEN)

if len(sys.argv) < 2:
    job_filename = input('Please enter job json filename: ')
else:
    job_filename = sys.argv[1]


def load_job_json(job_filename):
    job = {}
    with open(job_filename) as job_file:
        job = json.load(job_file)

    return job


def run_job(job_filename):
    job = load_job_json(job_filename)
    print('Job JSON:\n' + json.dumps(job, indent=2))

    build = start_build(job)
    print('\n\nBuild response:\n' + json.dumps(build, indent=2))
    build_details = get_build(build, job)

    if build['blocked']:
        build_result = unblock_build(job['pipeline'], build['number'])


def start_build(job):
    message = job['message'] or None

    return bk.builds().create_build(organization=ORG,
                                 pipeline=job['pipeline'],
                                 commit=job['commit'],
                                 branch=job['branch'],
                                 message=job['message'],
                                 ignore_pipeline_branch_filters=True)

    #r = requests.post(API_BASE_URL + 'pipelines/' + job['pipeline'] + '/builds',
    #                  json=payload, headers=HEADERS)
    #return json.loads(r.text)


def get_build(build):
    return bk.builds().get_build_by_number(organization=ORG,
                                           pipeline=build['pipeline']['slug'],
                                           build_number=build['number'])



def unblock_build(build):
    manual_steps = []
    for job in build['jobs']:
        if job['type'] == 'manual':
            manual_steps.append(job)

    for job in manual_steps:
        while job.get('state') == 'blocked':
            print("Blocked")
            break
    #    job_status = bk.jobs().get_job_log(ORG, build['pipeline']['slug'], build['number'], job_id)

    # while True:
    #     r = requests.get(API_BASE_URL + 'pipelines/' + pipeline + '/builds/' + build_number,
    #                      headers=HEADERS)
    #     build_status = json.loads(r.text)
    #     print('\n\nBuild status:\n' + json.dumps(build, indent=2))
    #     if build_status['blocked'] == 'false': break
    #     time.sleep(10)
    # job_id = build['jobs'][4]['id']
    # GET_JOB_LOG_URL = API_BASE_URL + 'pipelines/' + build['pipeline']['slug'] + '/builds/' + str(build['number']) + '/jobs/' + job_id + '/log'
    # r = requests.get(GET_JOB_LOG_URL, headers=HEADERS)

if __name__ == '__main__':
    print(f"Loading job details from file '{job_filename}'")
    job = load_job_json(job_filename)
    #run_job(job_filename)
