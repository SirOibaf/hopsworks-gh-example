import hopsworks
import argparse

parser = argparse.ArgumentParser(description="Utility deploy models on Hopsworks")
parser.add_argument("--name", help="Name of the model to deploy", required=True)
parser.add_argument(
    "--hopsworks-path",
    help="Path on Hopsworks where the predictor is stored",
    required=False,
    default="Resources",
)

args = parser.parse_args()

# Setup Model Registry API
project = hopsworks.login()
mr = project.get_model_registry()

# Deploy the best model according to the f1 score metric
model = mr.get_best_model("fraud_model_us", "f1score", "max")

deployment = model.deploy(
    name="fraud_model_us",
    model_server="PYTHON",
    # serving_tool="KSERVE",
    script_file=args.hopsworks_path,
)

print("Deployment: " + deployment.name)
deployment.describe()
