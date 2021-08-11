import os

from dotenv import load_dotenv
from invoke import task, Collection
from pathlib import Path
from github import Github


CONCOURSE_URL="http://localhost:8080"
PREFIX=""
CI_NAME = "training"

def run(c, cmd):
    """
    a wrapper to simplify debuging
    """
    SIZE = 50
    print("=" * SIZE)
    print(f"-> {cmd} <-")
    print("=" * SIZE)
    result = c.run(cmd)
    print("=" * SIZE)
    print(f"<- {cmd} ->")
    print("=" * SIZE)
    return result


@task
def run_ci(c):
    run(c, 'git submodule update --init --recursive')
    with c.cd('concourse-docker'):
        run(c, 'keys/generate')
        run(c, 'docker-compose up -d')

@task
def login(c):
    run(c, f'fly login -t {CI_NAME} -u test -p test -c {CONCOURSE_URL}')

@task
def open_browser(c):
    run(c, "open -a Google\\ Chrome " f"{CONCOURSE_URL}/?search={PREFIX}")
