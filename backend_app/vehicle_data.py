import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
import matplotlib.pyplot as plt
import io
import numpy as np
import pandas as pd
import seaborn as sns
import base64
from datetime import datetime

from typing import List, Dict, Any, Optional

from .db_mongo import FleetDatabase
from .utils import geodesic_km

plt.style.use('seaborn-v0_8')
sns.set_palette('husl')

class VehicleDataVisualizer:
    def __init__(self, uri : str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self._db = FleetDatabase(uri, db_name)

        self.numeric_fields = [
            'engine-speed', 'vehicle-speed', 'intake-manifold-absolute-pressure',
            'relative-throttle-position', 'commanded-throttle-actuator',
            'engine-coolant-temperature', 'accelerator-pedal-position',
            'drivers-demanded-torque', 'actual-engine-torque',
            'distance-traveled'
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
            'actual-engine-torque': 'Actual Engine Torque(%)',
            'distance-traveled': 'Distance Traveled (km)'
        }

    @property
    def db(self) -> FleetDatabase:
        """ Get database instance """
        return self._db

    def get_fields(self) -> Dict[str, str]:
        """ Get available fields"""
        return self.field_labels

    def compute_distance_traveled(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """Computes the daily distance traveled for each vehicle."""
        vehicles = self._db.get_all_vehicles()
        vehicles = self._db.get_vehicle_data(vehicles, start_date, end_date, True)

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

    def compute_daily_average(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """Computes average speed and distance traveled per day for each vehicle."""
        vehicles = self._db.get_all_vehicles()
        vehicles = self._db.get_vehicle_data(vehicles, start_date, end_date, True)

        if vehicles.empty:
            return pd.DataFrame()

        # Compute daily distances
        distance = self.compute_distance_traveled(start_date, end_date)

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


    def create_time_series_plot(self, units_id: List[str], field: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Creates a time series plot for the specified field and vehicles."""
        vehicles_data = self._db.get_vehicle_data(units_id, start_date, end_date, field == 'distance-traveled')

        if vehicles_data.empty or field not in vehicles_data.columns:
            return ""
    
        fig, ax = plt.subplots(figsize=(12, 6))
        for unit_id in units_id:
            data = vehicles_data[vehicles_data['unit-id'] == unit_id]
            if len(data) == 0:
                continue
            ax.plot(data['timestamp'], data[field], label=f'Unit {unit_id}', linewidth=2)
        
        ax.set_title(f"{self.field_labels.get(field, field)} Over Time", fontsize=14, fontweight='bold')
        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel(self.field_labels[field], fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.6)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_distribution_plot(self, units_id: List[str], field: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Creates hisotgram/distribution plot for the specified field and vehicles."""
        vehicles_data = self._db.get_vehicle_data(units_id, start_date, end_date, field == 'distance-traveled')
        if vehicles_data.empty or field not in vehicles_data.columns:
            return ""
        
        fig, ax = plt.subplots(figsize=(10, 6))

        for unit_id in units_id:
            data = vehicles_data[vehicles_data['unit-id'] == unit_id]
            if len(data) == 0:
                continue
            ax.hist(data[field], bins=30, alpha=0.5, label=f'Unit {unit_id}')
        
        ax.set_title(f"{self.field_labels[field]} Distribution", fontsize=14, fontweight='bold')
        ax.set_xlabel(self.field_labels[field], fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.6)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_box_plot(self, units_id: List[str], field: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Creates box plot for the specified field and vehicles."""
        vehicles_data = self._db.get_vehicle_data(units_id, start_date, end_date, field == 'distance-traveled')
        if vehicles_data.empty or field not in vehicles_data.columns:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))
        data_for_plot = []
        labels = []

        for unit_id in units_id:
            data = vehicles_data[vehicles_data['unit-id'] == unit_id]
            if len(data) == 0:
                continue
            data_no_na = data[field].dropna()
            if data_no_na.empty:
                continue
            data_for_plot.append(data_no_na)
            labels.append(f'Unit {unit_id}')

        if len(data_for_plot) == 0:
            return ""

        ax.boxplot(data_for_plot, tick_labels=labels)
        ax.set_title(f"{self.field_labels[field]} Comparison", fontsize=14, fontweight='bold')
        ax.set_ylabel(self.field_labels[field], fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig) -> bytes:
        """Convert a Matplotlib figure to base64-encoded PNG bytes."""
        image_buffer = io.BytesIO()
        fig.savefig(image_buffer, format='png', bbox_inches='tight')
        image_buffer.seek(0)
        img_str = base64.b64encode(image_buffer.getvalue()).decode()
        plt.close(fig)

        return img_str
