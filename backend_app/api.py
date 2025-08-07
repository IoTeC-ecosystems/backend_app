from flask import Blueprint, session

main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
def home():
    session.clear()

    return {"status": 200, "msg": "connected" }
