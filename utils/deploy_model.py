import hopsworks
import argparse

parser = argparse.ArgumentParser(description="Utility deploy models on Hopsworks")
parser.add_argument("--name", help="Name of the model to deploy", required=True)
parser.add_argument("--version", help="Version of the model to deploy", required=True)
parser.add_argument("--deployment-name", help="Name of the deployment", required=True)
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
model = mr.get_model(args.name, args.version)

deployment = model.deploy(
    name=args.deployment_name,
    model_server="PYTHON",
    # serving_tool="KSERVE",
    script_file="hdfs:///Projects/{}/{}".format(project.name, args.hopsworks_path),
)

print("Deployment: " + deployment.name)
deployment.describe()
