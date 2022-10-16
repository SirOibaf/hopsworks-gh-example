import hopsworks
import argparse
import json
import os

parser = argparse.ArgumentParser(description="Utility to submit jobs to Hopsworks")
parser.add_argument("--name", help="Name of the job", required=True)
parser.add_argument(
    "--path",
    help="Local path of the file to use as Job configuration",
    required=True,
)
parser.add_argument(
    "--hopsworks-path",
    help="Path on Hopsworks where the repository is cloned",
    required=False,
    default="Resources",
)
parser.add_argument(
    "--execute", help="Set True to execute the job", required=False, default=False
)
args = parser.parse_args()

# Setup Jobs API
project = hopsworks.login()
jobs_api = project.get_jobs_api()

# Read job Configuration
with open(args.path) as f:
    config = json.loads(f.read())

config["appPath"] = "hdfs:///Projects/{}/{}".format(project.name, args.hopsworks_path)
config["appName"] = args.name

# Create or update job
try:
    job = jobs_api.get_job(args.name)
except:
    job = jobs_api.create_job(args.name, config)

job.config = config
job.save()

if args.execute:
    # Run the job
    job.run(await_termination=True)
