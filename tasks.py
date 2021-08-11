import os

from dotenv import load_dotenv
from invoke import task, Collection
from pathlib import Path
from github import Github

load_dotenv()

CONCOURSE_URL="http://localhost:8080"
PREFIX="training"
CI_NAME = "training"
ga_token = os.getenv("GITHUB_ACCESS_TOKEN")

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

@task
def set_pipelines(c):
    for pipeline_name in ["on-merge"]:
        run(
            c,
            f'''fly -t {CI_NAME} set-pipeline \
            -c ./ci/{pipeline_name}.yml \
            -p {PREFIX}-{pipeline_name} \
            --var "GITHUB_ACCESS_TOKEN={ga_token}"'''
        )



@task
def create_deployment(c):
    # FIXME: create constants
    g = Github(ga_token)
    repo = g.get_repo("kharandziuk/concourse-tests")
    deployment = repo.create_deployment(ref="main", environment="staging")
    deployment.create_status(state="success",)

ns = Collection()

ci = Collection("ci")
ci.add_task(run_ci)
ci.add_task(login)
ci.add_task(set_pipelines)
ci.add_task(open_browser)

deployment = Collection("deployment")
deployment.add_task(create_deployment)

ns.add_collection(ci)
ns.add_collection(deployment)

