from flask import Blueprint, session
from flask_cors import CORS

main = Blueprint('main', __name__)

CORS(main, resources={r"/*": {"origins": "http://localhost:8000.*"}})

@main.route("/", methods=["GET", "POST"])
def home():
    session.clear()

    return {"status": 200, "msg": "connected" }
