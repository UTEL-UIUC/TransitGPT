import sys
import traceback
from rich.traceback import install as install_rich_traceback
from utils.gtfs_loader import GTFSLoader

## For Evals
import folium
import numpy as np
import pandas as pd
import geopandas as gpd
import time
import shapely
from shapely.geometry import Point, LineString, Polygon
import datetime
import matplotlib
import matplotlib.pyplot as plt
import plotly
import plotly.express as px

from prompts.generate_prompt import generate_system_prompt

install_rich_traceback()


class GTFS_Eval:
    def __init__(self, file_mapping, distance_unit="m"):
        self.feed_main = None
        self.gtfs = None
        self.system_prompt = None
        self.file_mapping = file_mapping
        self.distance_unit = distance_unit
        # Initialize GTFSLoader objects for each GTFS feed in the selectbox with feed_sfmta
        for key in self.file_mapping:
            file_location = self.file_mapping[key]
            setattr(
                self,
                f"feed_{key.lower()}",
                GTFSLoader(key, file_location, distance_unit),
            )

    def load_current_feed(self, GTFS):
        if not self.gtfs or self.gtfs != GTFS:
            feed_main = getattr(self, f"feed_{GTFS.lower()}")
            # Load all tables for the selected GTFS feed
            feed_main.load_all_tables()
            self.gtfs = GTFS
            print(f"Loaded feed {self.gtfs}")
        return feed_main

    def load_system_prompt(self, GTFS, distance_unit="m"):
        if (
            self.system_prompt is None
            or self.gtfs != GTFS
            or self.distance_unit != distance_unit
        ):
            if self.gtfs != GTFS:
                self.feed_main = self.load_current_feed(GTFS)
                self.gtfs = GTFS

            self.distance_unit = distance_unit
            self.system_prompt = generate_system_prompt(
                self.gtfs, self.feed_main, self.distance_unit
            )

        return self.system_prompt

    def evaluate(self, code):
        """
        Evaluates the given code and returns the result.

        Parameters:
            code (str): The code to be evaluated.

        Returns:
            tuple: A tuple containing the result of the evaluation, a boolean indicating if the evaluation was successful,
                   detailed error information if the evaluation failed, and a boolean indicating if response is only text.
        """
        # Format string input to extract only the code
        if "```python" in code:
            code = (
                code.split("```python")[1].split("```")[0]
                if "```python" in code
                else code
            )
        else:
            # Has no code block. Send back with only text response
            return (None, True, None, True)
        nm = globals()
        locals_dict = {
            "np": np,
            "pd": pd,
            "gpd": gpd,
            "plt": plt,
            "matplotlib": matplotlib,
            "folium": folium,
            "time": time,
            "datetime": datetime,
            "shapely": shapely,
            "Point": Point,
            "LineString": LineString,
            "Polygon": Polygon,
            "result": None,
            "px": px,
            "plotly": plotly,
        }
        nm.update(locals_dict)
        nm.update({"feed": self.feed_main})
        try:
            exec(code, nm)
            return (nm.get("result"), True, None, False)
        except Exception as e:
            error_info = self._get_detailed_error_info(e)
            return (None, False, error_info, False)

    def _get_detailed_error_info(self, error: Exception) -> str:
        """
        Get detailed error information including the full traceback and local variables.
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.extract_tb(exc_traceback)

        error_info = [
            "Detailed Error Information:",
            f"Error Type: {exc_type.__name__}",
            f"Error Message: {str(error)}",
            "Traceback (most recent call last):",
        ]

        for filename, line_num, func_name, text in tb_list:
            error_info.append(f"  File '{filename}', line {line_num}, in {func_name}")
            if text:
                error_info.append(f"    {text.strip()}")
        return "\n".join(error_info)
