from flask import Blueprint, session, jsonify
from flask_cors import CORS

from .vehicle_data import VehicleDataVisualizer

main = Blueprint('main', __name__)

CORS(main, resources={r"/*": {"origins": "http://localhost:8000.*"}})

visualizer = VehicleDataVisualizer()
db = visualizer.db

@main.route("/", methods=["GET", "POST"])
def home():
    session.clear()

    return {"status": 200, "msg": "connected" }


@main.route("/api/vehicles", methods=["GET"])
def get_vehicles():
    vehicles = db.get_all_vehicles()
    return jsonify({"status": 200, "data": vehicles})

