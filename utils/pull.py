import hopsworks

project = hopsworks.login()
git_api = project.get_git_api()

# Git repository to clone
provider = "GitHub"
url = "https://github.com/siroibaf/hopsworks-gh-example.git"
branch = "main"

# Dataset location where to clone the repository
folder = "Resources"

# Retrieve the repository metadata from Hopsworks
try:
    repo = git_api.get_repo("hopsworks-gh-example")
except:
    # Repository doesn't exists on Hopsworks. Clone it.
    repo = git_api.clone(url, folder, provider, branch=branch)

# Repository already exists on Hopsworks. Pull the latest changes.
repo.pull(branch)
