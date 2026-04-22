import json
import os
from threading import Lock

JOBS_FILE = "jobs.json"
file_lock = Lock()


def load_jobs():
    if not os.path.exists(JOBS_FILE):
        return {}

    with open(JOBS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_jobs(jobs: dict):
    with file_lock:
        with open(JOBS_FILE, "w") as f:
            json.dump(jobs, f, indent=2)
