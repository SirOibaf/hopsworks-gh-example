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
parser.add_argument(
    "--repository",
    help="Repository to clone in format {github organization}/{github repository}",
    required=False,
    default="siroibaf/hopsworks-gh-example",
)
parser.add_argument(
    "--branch",
    help="Branch to clone, in case of PR testing",
    required=False,
    default="main",
)
parser.add_argument(
    "--purge",
    help="Purge existing cloned repository",
    required=False,
    default=False,
)
args = parser.parse_args()

project = hopsworks.login()
git_api = project.get_git_api()

# Git repository to clone
provider = "GitHub"
url = "https://github.com/{}.git".format(args.repository)
branch = args.branch

# Dataset location where to clone the repository
folder = args.hopsworks_path

# Retrieve the repository metadata from Hopsworks
try:
    repo = git_api.get_repo("hopsworks-gh-example")

    if args.purge:
        # Need to purge existing repository
        repo.delete()
        repo = git_api.clone(url, folder, provider, branch=branch)

except:
    # Repository doesn't exists on Hopsworks. Clone it.
    repo = git_api.clone(url, folder, provider, branch=branch)

# Repository already exists on Hopsworks. Pull the latest changes.
repo.pull(branch)
