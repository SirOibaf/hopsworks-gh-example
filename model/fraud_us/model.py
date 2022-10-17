import hopsworks
import joblib
import numpy as np
import xgboost as xgb

from sklearn.metrics import f1_score
from hsml.schema import Schema
from hsml.model_schema import ModelSchema


def create_feature_view(fs, fv_name, fv_version):
    # Load the feature groups
    trans_fg = fs.get_feature_group("transactions", version=2)
    profiles_fg = fs.get_feature_group("profile", version=2)

    # Assemble feature view query
    query = (
        trans_fg.select_except(["tid", "cc_num", "datetime"])
        .join(profiles_fg.select_except(["cc_num"]))
        .filter(trans_fg.country == "US")
    )

    # Load the transformation functions.
    min_max_scaler = fs.get_transformation_function(name="min_max_scaler")
    label_encoder = fs.get_transformation_function(name="label_encoder")

    # Map features to transformation functions.
    transformation_functions = {
        "loc_delta_t_minus_1": min_max_scaler,
        "time_delta_t_minus_1": min_max_scaler,
        "country": label_encoder,
        "gender": label_encoder,
    }

    # Create feature view and return metadata
    return fs.create_feature_view(
        name=fv_name,
        version=fv_version,
        query=query,
        labels=["fraud_label"],
        transformation_functions=transformation_functions,
    )


def get_or_create_feature_view(fs, fv_name, fv_version):
    try:
        return fs.get_feature_view(name=fv_name, version=fv_version)
    except:
        return create_feature_view(fs, fv_name, fv_version)


def train_model(fv):
    # Get training dataset
    X_train, X_test, y_train, y_test = fv.train_test_split(
        test_size=0.3,
        description="Transactions fraud online training dataset",
        # statistics_config={"enabled": True, "histograms": True, "correlations": True},
    )

    # Train a XGBoost model
    clf = xgb.XGBClassifier()
    clf.fit(X_train, y_train)

    # Test prediction and compute f1score
    y_test_pred = clf.predict(X_test)
    metrics = {"f1score": f1_score(y_test, y_test_pred, average="micro")}

    # Model Schema
    model_schema = ModelSchema(
        input_schema=Schema(X_train), output_schema=Schema(y_train)
    )

    return clf, metrics, model_schema


def register_model(model, metrics, model_schema):
    joblib.dump(model, "model.pkl")

    model = mr.sklearn.create_model(
        name="fraud_model_us",
        metrics=metrics,
        description="Isolation forest anomaly detection model",
        model_schema=model_schema,
    )

    model.save("model.pkl")


if __name__ == "__main__":
    project = hopsworks.login()
    fs = project.get_feature_store()
    mr = project.get_model_registry()

    fv = get_or_create_feature_view(fs, "fraud_model_us", 1)
    model, metrics, model_schema = train_model(fv)

    register_model(model, metrics, model_schema)
