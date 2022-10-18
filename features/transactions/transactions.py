import hopsworks
import numpy as np
import pandas as pd
import logging
from math import radians


# Feature engineering.
def haversine(long, lat, shift):
    """Compute Haversine distance between each consecutive coordinate in (long, lat)."""

    long_shifted = long.shift(shift)
    lat_shifted = lat.shift(shift)
    long_diff = long_shifted - long
    lat_diff = lat_shifted - lat

    a = np.sin(lat_diff / 2.0) ** 2
    b = np.cos(lat) * np.cos(lat_shifted) * np.sin(long_diff / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a + b))

    return c


def time_delta(datetime_value, shift):
    """Compute time difference between each consecutive transaction."""

    time_shifted = datetime_value.shift(shift)
    return time_shifted


logging.info("Downloading profiles data")
profiles_df = pd.read_csv(
    "https://repo.hops.works/master/hopsworks-tutorials/data/card_fraud_online/profiles.csv",
    parse_dates=["birthdate"],
)
profiles_df.columns = [
    "name",
    "gender",
    "mail",
    "birthdate",
    "City",
    "Country",
    "cc_num",
]
profiles_df = profiles_df[["cc_num", "gender"]]

logging.info("Downloading transaction data")
trans_df = pd.read_csv(
    "https://repo.hops.works/master/hopsworks-tutorials/data/card_fraud_online/transactions.csv",
    parse_dates=["datetime"],
)

trans_df = trans_df[trans_df.category == "Cash Withdrawal"].reset_index(
    level=0, drop=True
)
trans_df["country"] = trans_df["country"].fillna("US")

profiles_df = profiles_df[
    profiles_df.cc_num.isin(trans_df.cc_num.unique())
].reset_index(level=0, drop=True)

trans_df["loc_delta_t_plus_1"] = (
    trans_df.groupby("cc_num")
    .apply(lambda x: haversine(x["longitude"], x["latitude"], 1))
    .reset_index(level=0, drop=True)
    .fillna(0)
)

trans_df["loc_delta_t_minus_1"] = (
    trans_df.groupby("cc_num")
    .apply(lambda x: haversine(x["longitude"], x["latitude"], -1))
    .reset_index(level=0, drop=True)
    .fillna(0)
)

trans_df["time_delta_t_minus_1"] = (
    trans_df.groupby("cc_num")
    .apply(lambda x: time_delta(x["datetime"], -1))
    .reset_index(level=0, drop=True)
)

trans_df["time_delta_t_minus_1"] = (
    trans_df.time_delta_t_minus_1 - trans_df.datetime
) / np.timedelta64(1, "D")
trans_df["time_delta_t_minus_1"] = trans_df.time_delta_t_minus_1.fillna(0)

trans_df.sort_values("datetime", inplace=True)

trans_df[["longitude", "latitude"]] = trans_df[["longitude", "latitude"]].applymap(
    radians
)
trans_df = trans_df[
    [
        "tid",
        "datetime",
        "cc_num",
        "amount",
        "country",
        "fraud_label",
        "loc_delta_t_plus_1",
        "loc_delta_t_minus_1",
        "time_delta_t_minus_1",
    ]
]

project = hopsworks.login()
fs = project.get_feature_store()

trans_fg = fs.get_or_create_feature_group(
    name="transactions",
    version=2,
    description="Transaction data",
    primary_key=["cc_num"],
    event_time="datetime",
    online_enabled=True,
    statistics_config={"enabled": True, "histograms": True, "correlations": True},
)
trans_fg.insert(trans_df)
