from datetime import datetime

from flask import Blueprint, session, jsonify, request
from flask_cors import CORS

from .vehicle_data import VehicleDataVisualizer

main = Blueprint('main', __name__)

CORS(main, resources={r"/*": {"origins": "http://localhost:8000.*"}})

visualizer = VehicleDataVisualizer()
db = visualizer.db

@main.route("/", methods=["GET", "POST"])
def home():
    session.clear()

    return {"status": 200, "data": "connected" }


@main.route("/api/vehicles", methods=["GET"])
def get_vehicles():
    vehicles = db.get_all_vehicles()
    return jsonify({"status": 200, "data": vehicles})



@main.route("/api/speed-over-time", methods=["POST"])
def speed_over_time():
    data = request.get_json()
    units_id = data.get("units_id", [])
    try:
        start_date = datetime.fromisoformat(data.get("start_time"))
    except TypeError:
        start_date = None
    try:
        end_date = datetime.fromisoformat(data.get("end_time"))
    except TypeError:
        end_date = None

    plot = visualizer.create_time_series_plot(
        units_id=units_id,
        field="vehicle-speed",
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})

    return jsonify({"status": 200, "data": plot})


@main.route("/api/daily-distance", methods=["POST"])
def daily_distance():
    data = request.get_json()
    units_id = data.get("units_id", [])
    try:
        start_date = datetime.fromisoformat(data.get("start_time"))
    except TypeError:
        start_date = None
    try:
        end_date = datetime.fromisoformat(data.get("end_time"))
    except TypeError:
        end_date = None

    plot = visualizer.plot_daily_distance(
        units_id=units_id,
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})

    return jsonify({"status": 200, "data": plot})