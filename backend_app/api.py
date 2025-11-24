from datetime import datetime

from flask import Blueprint, session, jsonify, request
from flask_cors import CORS

from .vehicle_data import VehicleDataVisualizer
from .utils import extract_fields

main = Blueprint('main', __name__)

CORS(main, resources={r"/*": {"origins": "http://localhost:5500.*"}})

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


@main.route("/api/fields", methods=["GET"])
def get_fields():
    fields = visualizer.get_fields()
    return jsonify({"status": 200, "data": fields})


@main.route("/api/speed-over-time", methods=["POST"])
def speed_over_time():
    data = request.get_json()
    units_id, start_date, end_date = extract_fields(data)

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
    units_id, start_date, end_date = extract_fields(data)

    plot = visualizer.plot_daily_distance(
        units_id=units_id,
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})

    return jsonify({"status": 200, "data": plot})


@main.route('/api/average-speed-distance', methods=['POST'])
def average_speed_distance():
    data = request.get_json()
    unit_id, start_date, end_date = extract_fields(data)

    plot = visualizer.plot_daily_average(
        unit_id=unit_id,
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})

    return jsonify({"status": 200, "data": plot})


@main.route("/api/plot/timeseries", methods=["POST"])
def plot_timeseries():
    data = request.get_json()
    units_id, start_date, end_date = extract_fields(data)
    field = data.get("field", "")
    if field == "":
        return jsonify({"status": 400, "data": "Field parameter is required."})

    plot = visualizer.create_time_series_plot(
        units_id=units_id,
        field=field,
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})

    return jsonify({"status": 200, "data": plot})


@main.route("/api/plot/distribution", methods=["POST"])
def plot_distribution():
    data = request.get_json()
    units_id, start_date, end_date = extract_fields(data)
    field = data.get("field", "")
    if field == "":
        return jsonify({"status": 400, "data": "Field parameter is required."})

    plot = visualizer.create_distribution_plot(
        units_id=units_id,
        field=field,
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})

    return jsonify({"status": 200, "data": plot})


@main.route("/api/plot/boxplot", methods=["POST"])
def plot_boxplot():
    data = request.get_json()
    units_id, start_date, end_date = extract_fields(data)
    field = data.get("field", "")
    if field == "":
        return jsonify({"status": 400, "data": "Field parameter is required."})

    plot = visualizer.create_box_plot(
        units_id=units_id,
        field=field,
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})

    return jsonify({"status": 200, "data": plot})


@main.route("/api/plot/scatter", methods=["POST"])
def plot_scatter():
    data = request.get_json()
    units_id, start_date, end_date = extract_fields(data)
    field_x = data.get("field_x", "")
    field_y = data.get("field_y", "")
    if field_x == "" or field_y == "":
        return jsonify({"status": 400, "data": "Both field_x and field_y parameters are required."})
    
    plot = visualizer.create_scatter_plot(
        units_id=units_id,
        field_x=field_x,
        field_y=field_y,
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})
    
    return jsonify({"status": 200, "data": plot})


@main.route("/api/plot/heatmap", methods=["POST"])
def plot_heatmap():
    data = request.get_json()
    unit_id, start_date, end_date = extract_fields(data)

    if not unit_id:
        return jsonify({"status": 400, "data": "unit_id parameter is required."})
    
    plot = visualizer.create_correlation_heatmap(
        unit_id=unit_id,
        start_date=start_date,
        end_date=end_date
    )

    if plot == "":
        return jsonify({"status": 400, "data": "No data available for the selected parameters."})

    return jsonify({"status": 200, "data": plot})
