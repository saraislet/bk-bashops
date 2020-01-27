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

* Create Buildkite token at https://buildkite.com/user/api-access-tokens
  * Scope: read_builds, write_builds, read_pipelines
  * (Optional) put Buildkite API Token in `BUILDKITE_TOKEN`
* Write a sequence of Buildkite tasks in a JSON file. See `example_build_tasks.json`
* Run script with `python3 bk_bashops.py [filename]`

**There is a blocking error in pybuildkite fixed by a fork**

## **pybuildkite issue:**
Until [PyBuildkite is fixed](https://github.com/pyasi/pybuildkite/pull/35), clone the [working fork](https://github.com/Saraislet/pybuildkite/tree/fix-jobs-base-url) and load pybuildkite from that path:
```bash
$ git clone git@github.com:Saraislet/pybuildkite.git
$ cd pybuldkite
$ git checkout fix-jobs-base-url
```

And modify `run_build_task.py` to load from the path cloned above, [as shown here](https://github.com/PagerDuty/security-scripts/blob/1d358add519a6059b9b43678fc84c17e0fd42b05/bk_bashops/run_build_task.py#L7-L8)
```python
sys.path.insert(0, 'path_to/pybuildkite')
from pybuildkite.buildkite import Buildkite, BuildState
```

## Unblocking configuration

Script can bypass blocking steps.

If the keys for unblock steps are entered in `unblock_fields.json` or in the task queue, their values will be given to the Buildkite job when needed. If the value for a key is blank, it will be requested when it comes up during the job.

The expected key-value pairs for blocking steps can be found in the buildkite script for that pipeline. E.g., https://github.com/PagerDuty/chef/blob/c0d47acfe3e5a423bcbc365e01d06359aa510354/.buildkite/lock_check.sh#L31-L36

**Flaws of the current unblocking design:**

* Script assumes each build has a single blocking step with the values listed.
* Blank values are not requested at the beginning of the run but in the middle, when the blocking step is reached.
* General danger of not confirming each lock and unblock individually but from a script. Script could begin with listing each unblock and requesting either values or confirmation of value from task queue.

# Notes

* Script has minimal error-handling.

