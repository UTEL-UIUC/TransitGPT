import gtfs_kit as gk
import pandas as pd
import numpy as np
import zipfile
import datetime
import traceback
from typing import Optional, Any
from functools import lru_cache, partial
from utils.helper import list_files_in_zip
from geopy.distance import geodesic

DATE_FORMAT = "%Y%m%d"
DATE_FORMAT_ALT = "%Y-%m-%d"

class GTFSLoader:
    def __init__(self, gtfs, gtfs_path: str, distance_unit: str = "km"):
        self.gtfs = gtfs
        self.gtfs_path = gtfs_path
        self.feed: Optional[gk.feed] = None
        self.file_list = list_files_in_zip(gtfs_path)
        self.zipfile = zipfile.ZipFile(gtfs_path)
        self.distance_unit = distance_unit

    def __getstate__(self):
        state = self.__dict__.copy()
        if "zipfile" in state:
            del state["zipfile"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def load_feed(self):
        try:
            feed = gk.read_feed(self.gtfs_path, dist_units=self.distance_unit)
            feed = self._process_feed(feed)
            self.feed = feed
        except Exception as e:
            print(f"Error loading GTFS feed: {e}")
            print(traceback.format_exc())
            return False
        return True

    def _process_feed(self, feed):
        feed = self._append_distances(feed)
        feed = feed.clean()
        feed = self._parse_times_and_dates(feed)
        feed = self._remove_empty_attributes(feed)
        return feed

    def _append_distances(self, feed):
        if "shape_dist_traveled" not in feed.shapes.columns or feed.shapes.shape_dist_traveled.isna().any():
            feed = self._calculate_shape_distances(feed)
        # if "shape_dist_traveled" not in feed.stop_times.columns or feed.stop_times.shape_dist_traveled.isna().any():
        #     feed = self._calculate_stop_distances(feed)
        return feed

    def _calculate_shape_distances(self, feed):
        print("Calculating shape distances")
        
        results = []
        for _, group in feed.shapes.groupby('shape_id'):
            result = self._calculate_single_shape(group, self.distance_unit)
            results.append(result)
        
        # Combine the results
        feed.shapes = pd.concat(results)
        
        return feed

    def _calculate_single_shape(self, group, distance_unit):
        cumulative_distance = 0
        previous_point = None
        
        for idx, row in group.iterrows():
            current_point = (row['shape_pt_lat'], row['shape_pt_lon'])
            
            if previous_point is not None:
                distance = geodesic(previous_point, current_point).meters
                if distance_unit == 'km':
                    distance /= 1000
                elif distance_unit == 'miles':
                    distance *= 0.000621371
                cumulative_distance += distance
            
            group.at[idx, 'shape_dist_traveled'] = cumulative_distance
            previous_point = current_point
        
        return group

    def _calculate_stop_distances(self, feed):
        print("Calculating stop distances")
        stops = feed.stops.set_index('stop_id')
        
        for trip_id, group in feed.stop_times.groupby('trip_id'):
            cumulative_distance = 0
            previous_stop = None
            
            for idx, row in group.iterrows():
                current_stop = stops.loc[row['stop_id']]
                
                if previous_stop is not None:
                    distance = geodesic(
                        (previous_stop.stop_lat, previous_stop.stop_lon),
                        (current_stop.stop_lat, current_stop.stop_lon)
                    ).meters
                    if self.distance_unit == 'km':
                        distance /= 1000
                    elif self.distance_unit == 'miles':
                        distance *= 0.000621371
                    
                    cumulative_distance += distance
                
                feed.stop_times.at[idx, 'shape_dist_traveled'] = cumulative_distance
                previous_stop = current_stop
        
        return feed

    def _parse_times_and_dates(self, feed):
        vparse_time = np.vectorize(self.parse_time)
        vparse_date = np.vectorize(self.parse_date)

        feed.stop_times[["departure_time", "arrival_time"]] = feed.stop_times[["departure_time", "arrival_time"]].apply(vparse_time)
        
        if hasattr(feed, "timeframes"):
            feed.timeframes[["start_time", "end_time"]] = feed.timeframes[["start_time", "end_time"]].apply(vparse_time)
        
        for attr in ["calendar", "calendar_dates", "feed_info"]:
            if hasattr(feed, attr) and isinstance(getattr(feed, attr), pd.DataFrame):
                df = getattr(feed, attr)
                date_columns = [col for col in df.columns if "date" in col.lower()]
                df[date_columns] = df[date_columns].apply(vparse_date)
                setattr(feed, attr, df)

        return feed

    def _remove_empty_attributes(self, feed):
        for attr in dir(feed):
            if not attr.startswith('_'):
                value = getattr(feed, attr)
                if value is None or (isinstance(value, pd.DataFrame) and value.empty):
                    try:
                        delattr(feed, attr)
                    except Exception:
                        pass
        return feed

    @lru_cache(maxsize=None)
    def load_all_tables(self):
        if not self.feed and not self.load_feed():
            return

        for table in self.file_list:
            table_name = table.split(".")[0]
            if not hasattr(self.feed, table_name):
                try:
                    with self.zipfile.open(f"{table_name}.txt", "r") as f:
                        df = pd.read_csv(f, encoding="utf-8")
                        setattr(self.feed, table_name, df)
                except Exception as e:
                    print(f"Could not load {table_name} due to {e}")

        print(f"Loaded all tables: {self.gtfs}")
        if hasattr(self, "zipfile"):
            del self.zipfile

    @lru_cache(maxsize=2**18)
    def parse_time(self, val: Any) -> np.float32:
        if isinstance(val, (float, np.float32)) or pd.isna(val):
            return val
        if not val:
            return np.nan
        try:
            return np.float32(val)
        except ValueError:
            h, m, s = map(float, str(val).strip().split(":"))
            return np.float32(h * 3600 + m * 60 + s)

    @lru_cache(maxsize=2**18)
    def parse_date(self, val: str) -> datetime.date:
        if isinstance(val, datetime.date):
            return val
        for date_format in [DATE_FORMAT, DATE_FORMAT_ALT]:
            try:
                return datetime.datetime.strptime(val, date_format).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {val}")
