This script allows running a sequence of builds in Buildkite from the command line.

**Caution: use with care**. This script can override a lock held by someone else and deploy dangerous actions.

# Features

* immediately confirms that user holds any necessary lock
* can auto-bypasses the lock confirmation from Buildkite
* can enter any necessary values such as converge/pause search strings to unblock Buildkite jobs without user interaction
* missing values in block steps will be requested if known (otherwise will error out)
* will read BUILDKITE_TOKEN from environment variable or request token and hide entry
* can read a sequence of build tasks from a file entered as command-line argument, or request a choice of json file to run
* shows the build that it will run just before running, but doesn't confirm

# Setup

Script uses [f-strings](https://realpython.com/python-f-strings/) and requires Python 3.6+! Sorry not sorry.

* Set ORG in `run_build_task.py` to your organization's slug
* Create Buildkite token at https://buildkite.com/user/api-access-tokens
  * Scope: read_builds, write_builds, read_pipelines
  * (Optional) put Buildkite API Token in `BUILDKITE_TOKEN`
* Write a sequence of Buildkite tasks in a JSON file. See `example_build_tasks.json`
* Run script with `python3 bk_bashops.py [filename]`
* Install [PyBuildkite](https://github.com/pyasi/pybuildkite), e.g. with `pip install pybuildkite`

## Unblocking configuration

Script can bypass blocking steps.

If the keys for unblock steps are entered in `unblock_fields.json` or in the task queue, their values will be given to the Buildkite job when needed. If the value for a key is blank, it will be requested when it comes up during the job.

The expected key-value pairs for blocking steps can be found in the buildkite script for that pipeline. See Buildkite documentation on [block steps](https://buildkite.com/docs/pipelines/block-step). E.g., from the following example, the key and one potential value would be `{"release-stream": "stable"}`
```yaml
steps:
  - block: "Request Release"
    fields:
      - select: "Stream"
        key: "release-stream"
        options:
          - label: "Beta"
            value: "beta"
          - label: "Stable"
            value: "stable"
```

**Flaws of the current unblocking design:**

* Script assumes each build has a single blocking step with the values listed.
* Blank values are not requested at the beginning of the run but in the middle, when the blocking step is reached.
* General danger of not confirming each lock and unblock individually but from a script. Script could begin with listing each unblock and requesting either values or confirmation of value from task queue.

# Notes

* Script has minimal error-handling.

