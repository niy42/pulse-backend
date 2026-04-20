import json

FILE_PATH = "users.json"


def load_users():
    try:
        with open(FILE_PATH) as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    with open(FILE_PATH, "w") as f:
        json.dump(users, f)
