import os
import shutil
from os.path import expanduser
from pwd import getpwnam
from git import Repo
from tljh.hooks import hookimpl

def clone_repo(user, git_url, branch_name, repo_dir):
    """
    A function to clone a github repo into a specific directory of a given user.
    User receiver owner rights of all files in the repository
    """
    clone_options = []
    if branch_name is not None:
        clone_options.append([f"--branch {branch_name}"])

    Repo.clone_from(git_url, repo_dir, multi_options=clone_options)
    uid = getpwnam(user).pw_uid
    gid = getpwnam(user).pw_gid
    for root, dirs, files in os.walk(repo_dir):
        for d in dirs:
            shutil.chown(os.path.join(root, d), user=uid, group=gid)
        for f in files:
            shutil.chown(os.path.join(root, f), user=uid, group=gid)


@hookimpl
def tljh_new_user_create(username):
    """
    A function to clone a github repo into a 'repos' directory for every
    JupyterHub user when the server spawns a new notebook instance.
    """
    user_root_dir = expanduser(f"~{username}")
    # get repo url from environment variable
    git_url = os.getenv("REPO_URL")
    # nothing to do if no repo is specified
    if git_url is None:
        return

    branch_name = os.getenv("REPO_BRANCH")

    repo_collection_subdir = os.getenv("REPO_DST")
    if repo_collection_subdir is not None:
        repo_dir = os.path.join(user_root_dir, repo_collection_subdir)
    else:
        repo_dir = os.path.join(user_root_dir, repo_collection_subdir)

    if not os.path.isdir(repo_dir):
        os.makedirs(repo_dir)
        clone_repo(username, git_url, branch_name, repo_dir)
    else:
        # user already has the repo downloaded
        pass
