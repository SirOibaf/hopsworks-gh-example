import hopsworks
import pandas as pd
import logging

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

project = hopsworks.login()
fs = project.get_feature_store()

profile_fg = fs.get_or_create_feature_group(
    name="profile",
    version=2,
    description="Credit card holder demographic data",
    primary_key=["cc_num"],
    online_enabled=True,
    statistics_config={"enabled": True, "histograms": True, "correlations": True},
)
profile_fg.insert(profiles_df)
