from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

class FleetDatabase:
    def __init__(self, uri : str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.vehicles = self.db['vehicles']

    def get_all_vehicles(self) -> List[str]:
        """Return all the vehicles IDs from the database."""
        return self.vehicles.distinct("unit-id")

    def get_vehicle_data(self, units_ids: List[str], start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve data for the specified vehicles within the given time range."""
        query = {"unit-id": {"$in": units_ids}}

        if start_time and end_time:
            query["timestamp"] = {"$gte": start_time, "$lte": end_time}
        elif start_time:
            query["timestamp"] = {"$gte": start_time}
        elif end_time:
            query["timestamp"] = {"$lte": end_time}
        
        vehicles_data = self.vehicles.find(query)
        data = list(vehicles_data)

        if not data:
            return pd.DataFrame()
        
        vehicles_df = pd.DataFrame(data)
        vehicles_df['timestamp'] = pd.to_datetime(vehicles_df['timestamp'])
        return vehicles_df
    
    def get_range_data(self, unit_ids: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Get data for vehicles within a specific date range."""
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

        return self.get_vehicle_data(unit_ids, start_datetime, end_datetime)
