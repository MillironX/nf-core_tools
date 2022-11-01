#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for tests
"""

import functools
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

import requests

OLD_TRIMGALORE_SHA = "06348dffce2a732fc9e656bdc5c64c3e02d302cb"
OLD_TRIMGALORE_BRANCH = "mimic-old-trimgalore"
GITLAB_URL = "https://gitlab.com/nf-core/modules-test.git"
GITLAB_REPO = "nf-core"
GITLAB_DEFAULT_BRANCH = "main-restructure"
# Branch test stuff
GITLAB_BRANCH_TEST_BRANCH = "branch-tester-restructure"
GITLAB_BRANCH_TEST_OLD_SHA = "bce3f17980b8d1beae5e917cfd3c65c0c69e04b5"
GITLAB_BRANCH_TEST_NEW_SHA = "2f5f180f6e705bb81d6e7742dc2f24bf4a0c721e"


def with_temporary_folder(func):
    """
    Call the decorated funtion under the tempfile.TemporaryDirectory
    context manager. Pass the temporary directory name to the decorated
    function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with tempfile.TemporaryDirectory() as tmpdirname:
            return func(*args, tmpdirname, **kwargs)

    return wrapper


def with_temporary_file(func):
    """
    Call the decorated funtion under the tempfile.NamedTemporaryFile
    context manager. Pass the opened file handle to the decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with tempfile.NamedTemporaryFile() as tmpfile:
            return func(*args, tmpfile, **kwargs)

    return wrapper


@contextmanager
def set_wd(path: Path):
    """Sets the working directory for this context.

    Arguments
    ---------

    path : Path
        Path to the working directory to be used iside this context.
    """
    start_wd = Path().absolute()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(start_wd)


def mock_api_calls(mock, module, version):
    """Mock biocontainers and anaconda api calls for module"""
    biocontainers_api_url = f"https://quay.io/api/v1/repository/biocontainers/{module}/tag"
    anaconda_api_url = f"https://api.anaconda.org/package/bioconda/{module}"
    anaconda_mock = {
        "status_code": 200,
        "latest_version": version,
        "summary": "",
        "doc_url": "",
        "dev_url": "",
        "files": [{"version": version}],
        "license": "",
    }
    biocontainers_mock = {
        "tags": [
            {
                "name": version,
                "reversion": False,
                "start_ts": 1627050462,
                "manifest_digest": "sha256:3c986513543ace0d0456d51f4a5e4c254065fa665b47f7ed2fe01ed23e406608",
                "is_manifest_list": False,
                "size": 343605278,
                "last_modified": "Fri, 23 Jul 2021 14:27:42 -0000",
            }
        ],
        "page": 1,
        "has_additional": True,
    }

    mock.register_uri("GET", anaconda_api_url, json=anaconda_mock)
    mock.register_uri("GET", biocontainers_api_url, json=biocontainers_mock)


def check_pr_merged(repo, pr_number) -> bool:
    """
    Returns True if PR has been merged
    Returns False if PR has NOT been merged
    """
    pr_endpoint = f"https://api.github.com/repos/nf-core/{repo}/pulls/{pr_number}"

    response = requests.get(pr_endpoint)

    if response.status_code == 200:
        return response.json()["merged"] == "true"
    else:
        raise ValueError(f"Couldn't connect to GitHub API")
