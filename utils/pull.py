import hopsworks
import argparse

parser = argparse.ArgumentParser(
    description="Utility to pull repositories on Hopsworks"
)
parser.add_argument(
    "--hopsworks-path",
    help="Path on Hopsworks where the repository is cloned",
    required=False,
    default="Resources",
)
args = parser.parse_args()

project = hopsworks.login()
git_api = project.get_git_api()

# Git repository to clone
provider = "GitHub"
url = "https://github.com/siroibaf/hopsworks-gh-example.git"
branch = "main"

# Dataset location where to clone the repository
folder = args.hopsworks_path

# Retrieve the repository metadata from Hopsworks
try:
    repo = git_api.get_repo("hopsworks-gh-example")
except:
    # Repository doesn't exists on Hopsworks. Clone it.
    repo = git_api.clone(url, folder, provider, branch=branch)

# Repository already exists on Hopsworks. Pull the latest changes.
repo.pull(branch)
