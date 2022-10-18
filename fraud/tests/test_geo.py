import pandas as pd
import numpy as np

from fraud.features.utils.geo import haversine


class TestGeo:
    def test_haversine(self):
        data = {
            "latitude": [-34.83333, 49.0083899664],
            "longitude": [-58.5166646, 2.53844117956],
        }

        df = pd.DataFrame(data)

        distances = haversine(df["longitude"], df["latitude"], 1).tolist()

        assert np.isnan(distances[0])
        # Multiply by Earth radius to get KM
        assert int(distances[1] * 6371000 / 1000) == 11279

    def test_haversine_single(self):
        # Test that a single transaction doesn't break the method
        # i.e. there is no other transaction to compute the distance from

        data = {"latitude": [42.30865], "longitude": [-83.48216]}

        df = pd.DataFrame(data)

        distances = haversine(df["longitude"], df["latitude"], 1).tolist()

        assert np.isnan(distances[0])
