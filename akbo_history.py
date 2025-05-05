import pickle, os


def load_last_id(username, base="./history"):
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, f"{username}.pkl")
    if os.path.isfile(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


def save_last_id(username, last_id, base="./history"):
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, f"{username}.pkl"), "wb") as f:
        pickle.dump(last_id, f)