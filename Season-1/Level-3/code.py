from pathlib import Path

from flask import Flask, request
from werkzeug.security import safe_join

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent


@app.route("/")
def source():
    taxpayer = TaxPayer('foo', 'bar')
    path = request.args["input"]
    taxpayer.get_tax_form_attachment(path)
    taxpayer.get_prof_picture(path)
    return "", 204


def _read_local_file(path):
    candidate = (BASE_DIR / path).resolve()
    if not candidate.is_relative_to(BASE_DIR):
        return None
    relative_path = candidate.relative_to(BASE_DIR).as_posix()
    safe_path = safe_join(str(BASE_DIR), relative_path)
    if safe_path is None or not candidate.is_file():
        return None
    candidate.read_bytes()
    return str(candidate)


class TaxPayer:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.prof_picture = None
        self.tax_form_attachment = None

    def get_prof_picture(self, path=None):
        if not path:
            return None
        return _read_local_file(path)

    def get_tax_form_attachment(self, path=None):
        if not path:
            raise ValueError("Error: Tax form is required for all users")
        return _read_local_file(path)
