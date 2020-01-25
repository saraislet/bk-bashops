import json
import os
import requests
import sys

# Requires Python 3.6+ (because fstrings <3)
#
# Run with this command:
# python3 run_job.py job.json
#
# Create Buildkite API tokens here:
# https://buildkite.com/user/api-access-tokens
TOKEN = os.environ['BUILDKITE_TOKEN']

if len(sys.argv) < 2:
    job_file = input("Please enter job json filename: ")
else:
    job_file = sys.argv[1]

if __name__ == '__main__':
    print(f"Loading job details from file '{job_file}'")

