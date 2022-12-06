import hopsworks
import argparse

parser = argparse.ArgumentParser(
    description="Utility to install the necessary dependencies in the environment"
)
parser.add_argument(
    "--requirements-path",
    help="Path on Hopsworks where the requirements file is available",
)
parser.add_argument(
    "--wheel-name",
    help="Name of the project wheel to install",
)
parser.add_argument(
    "--wheel-path",
    help="Path on Hopsworks where the project wheel file is going to be uploaded",
)

args = parser.parse_args()

project = hopsworks.login()
environment_api = project.get_environment_api()
dataset_api = project.get_dataset_api()

# Purge existing environment
try:
    env = environment_api.get_environment()
    env.delete()
except:
    # The environment doesn't exists. No need to delete it
    pass

# Re-create the environment
environment_api.create_environment()

# Fetch new environment
env = environment_api.get_environment()

# Install requirements.txt
env.install_requirements(args.requirements_path)

# Install project module
# Remove existing wheel on the project
wheel_path = "{}/{}".format(args.wheel_path, args.wheel_name)
if dataset_api.exists(wheel_path):
    dataset_api.remove(wheel_path)

# Upload the new wheel
dataset_api.upload(args.wheel_name, args.wheel_path)

# Install the wheel
env.install_wheel(wheel_path)