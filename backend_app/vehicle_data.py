import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from typing import List, Dict, Any

from .db_mongo import FleetDatabase
from .utils import geodesic_km

plt.style.use('seaborn-v0_8')
sns.set_palette('husl')

class VehicleDataVisualizer:
    def __init__(self, uri : str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.db = FleetDatabase(uri, db_name)

        self.numeric_fields = [
            'engine-speed', 'vehicle-speed', 'intake-manifold-absolute-pressure',
            'relative-throttle-position', 'commanded-throttle-actuator',
            'engine-coolant-temperature', 'accelerator-pedal-position',
            'drivers-demanded-torque', 'actual-engine-torque'
        ]
        
        self.field_labels = {
            'engine-speed': 'Engine Speed (RPM)',
            'vehicle-speed': 'Vehicle Speed (km/h)',
            'intake-manifold-absolute-pressure': 'Intake Manifold Pressure (kPa)',
            'relative-throttle-position': 'Relative Throttle Position (%)',
            'commanded-throttle-actuator': 'Commanded Throttle Actuator (%)',
            'engine-coolant-temperature': 'Engine Coolant Temperature (%)',
            'accelerator-pedal-position': 'Accelerator Pedal Position (%)',
            'drivers-demanded-torque': 'Driver\'s Demanded Torque (%)',
            'actual-engine-torque': 'Actual Engine Torque(%)'
        }

    def get_fields(self) -> Dict[str, str]:
        """ Get available fields"""
        return self.field_labels

    def compute_distance_traveled(self):
        """Computes the daily distance traveled for each vehicle."""
        vehicles = self.db.get_all_vehicles()
        vehicles = self.db.get_vehicle_data(vehicles)

        if vehicles.empty:
            return pd.DataFrame()

        vehicles['date'] = vehicles['timestamp'].dt.date
        vehicles = vehicles.sort_values(by=['unit-id', 'timestamp'])

        daily_distances = []
        for unit_id in vehicles['unit-id'].unique():
            unit_data = vehicles[vehicles['unit-id'] == unit_id].copy()

            for date in unit_data['date'].unique():
                day_data = unit_data[unit_data['date'] == date].copy()
                if len(day_data) < 2:
                    daily_distances.append({
                        'unit-id': unit_id,
                        'date': date,
                        'distance_km': 0.0
                    })
                    continue
                total_distance = 0.0
                for i in range(1, len(day_data)):
                    point_a = (day_data.iloc[i-1]['latitude'], day_data.iloc[i-1]['longitude'])
                    point_b = (day_data.iloc[i]['latitude'], day_data.iloc[i]['longitude'])
                    distance = geodesic_km(point_a, point_b)
                    if np.isnan(distance):
                        continue
                    total_distance += distance
                daily_distances.append({
                    'unit-id': unit_id,
                    'date': date,
                    'distance_km': total_distance
                })

        return pd.DataFrame(daily_distances)

    def compute_daily_average(self):
        """Computes average speed and distance traveled per day for each vehicle."""
        vehicles = self.db.get_all_vehicles()
        vehicles = self.db.get_vehicle_data(vehicles)

        if vehicles.empty:
            return pd.DataFrame()

        # Compute daily distances
        distance = self.compute_distance_traveled()

        # Compute daily average speeds
        vehicles['date'] = vehicles['timestamp'].dt.date
        speed_avg = vehicles.groupby(['unit-id', 'date'])['speed'].mean().reset_index()
        speed_avg.columns = ['unit-id', 'date', 'avg_speed']
        if not distance.empty:
            result = pd.merge(speed_avg, distance, on=['unit-id', 'date'], how='outer')
            result['distance_km'] = result['distance_km'].fillna(0.0)
        else:
            result = speed_avg
            result['avg_speed'] = result['avg_speed'].fillna(0.0)

        return result
