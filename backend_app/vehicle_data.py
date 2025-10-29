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

    def plot_daily_distance(self, units_id: List[str], start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Creates a plot for daily distance traveled for the specified vehicles."""
        daily_distance = self.compute_distance_traveled(start_date, end_date)
        if daily_distance.empty:
            return ""

        fig, ax = plt.subplots(figsize=(12, 6))
        for unit_id in units_id:
            data = daily_distance[daily_distance['unit-id'] == unit_id]
            if len(data) == 0:
                continue
            ax.plot(data['date'], data['distance_km'], marker='o', label=f'Unit {unit_id}', linewidth=2)

        if len(ax.lines) == 0:
            return ""

        ax.set_title("Daily Distance Traveled", fontsize=14, fontweight='bold')
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Distance Traveled (km)", fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.6)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def plot_daily_average(self, unit_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Creates a plot for daily average speed and distance traveled for the specified vehicle."""
        daily_avg = self.compute_daily_average(start_date, end_date)
        if daily_avg.empty:
            return ""

        vehicle_data = daily_avg[daily_avg['unit-id'] == unit_id]
        if vehicle_data.empty:
            return ""

        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        axes[0].hist(vehicle_data['avg_speed'].dropna(), bins=20, color='skyblue', edgecolor='black')
        axes[0].set_title("Average Speed Distribution", fontsize=12, fontweight='bold')
        axes[0].set_xlabel("Time", fontsize=10)
        axes[0].set_ylabel("Average Speed (km/h)", fontsize=10)
        axes[0].grid(True, alpha=0.6)

        axes[1].hist(vehicle_data['distance_km'].dropna(), bins=20, color='salmon', edgecolor='black')
        axes[1].set_title("Distance Traveled Distribution", fontsize=12, fontweight='bold')
        axes[1].set_xlabel("Time", fontsize=10)
        axes[1].set_ylabel("Distance Traveled (km)", fontsize=10)
        axes[1].grid(True, alpha=0.6)

        fig.suptitle("Daily Average Speed and Distance Traveled", fontsize=14, fontweight='bold')

        plt.tight_layout()
        return self._fig_to_base64(fig)

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
    
    def create_scatter_plot(self, units_id: List[str], field_x: str, field_y: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Creates scatter plot for the specified fields and vehicles."""
        vehicles_data = self._db.get_vehicle_data(units_id, start_date, end_date, False)

        if vehicles_data.empty or field_x not in vehicles_data.columns or field_y not in vehicles_data.columns:
            return ""

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(units_id)))

        for i, unit_id in enumerate(units_id):
            data = vehicles_data[vehicles_data['unit-id'] == unit_id]
            try:
                ax.scatter(data[field_x], data[field_y], alpha=0.6, label=f'Unit {unit_id}', color=colors[i])
            except TypeError:
                return ""
        
        ax.set_title(f"{self.field_labels.get(field_x, field_x)} vs {self.field_labels.get(field_y, field_y)}", fontsize=14, fontweight='bold')
        ax.set_xlabel(self.field_labels.get(field_x, field_x), fontsize=12)
        ax.set_ylabel(self.field_labels.get(field_y, field_y), fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.6)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_correlation_heatmap(self, unit_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """Creates a correlation heatmap for numeric fields of the specified vehicles."""
        vehicles_data = self._db.get_vehicle_data([unit_id], start_date, end_date, False)

        if vehicles_data.empty:
            return ""

        # Do not create if NA values are present
        try:
            # All fields but 'distance-traveled'
            corr_matrix = vehicles_data[self.numeric_fields[:-1]].corr()
        except TypeError:
            return ""

        fig, ax = plt.subplots(figsize=(12, 10))
        # Create heatmap
        im = ax.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        # Set ticks and labels
        ax.set_xticks(range(len(corr_matrix.columns)))
        ax.set_yticks(range(len(corr_matrix.columns)))
        ax.set_xticklabels([self.field_labels[col] for col in corr_matrix.columns], rotation=45, ha='right')
        ax.set_yticklabels([self.field_labels[col] for col in corr_matrix.columns])

        # Add correlation values
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', ha="center", va="center", color="black", fontweight='bold')

        title = f'Engine Parameters Correlation Matrix'
        title += f' - Vehicle {unit_id}'
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Correlation Coefficient', rotation=270, labelpad=15)
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
