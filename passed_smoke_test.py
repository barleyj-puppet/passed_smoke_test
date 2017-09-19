#!/usr/bin/env python
import json
import logging
import os

import click
import git
import jenkins

from lib.repo import Repo, EnterpriseDist, PeModulesVanagon
from lib.releases import releases


logging.basicConfig(level=logging.INFO)


jenkins_username = os.environ['JENKINS_USERNAME']
jenkins_token = os.environ['JENKINS_TOKEN']

def parse_build_description(description):
    return description.split('-')[-1][1:]


def get_latest_build(named_branch):
    branch = releases['default'][named_branch]
    server = jenkins.Jenkins('https://cinext-jenkinsmaster-enterprise-prod-1.delivery.puppetlabs.net', username=jenkins_username, password=jenkins_token)

    job_name = 'enterprise_pe-acceptance-tests_integration-system_pe_smoke-upgrade_{}'.format(branch)
    last_build = server.get_job_info(job_name)['lastCompletedBuild']
    build_info = server.get_build_info(job_name, last_build['number'])
    build_description = build_info['description']
    git_sha = parse_build_description(build_description)

    return git_sha


@click.group()
def cli():
    pass


@cli.command()
@click.option("--repo")
@click.option("--branch")
def commits(repo, branch):
    vanagon = PeModulesVanagon(branch)
    commits = vanagon.commits(repo)

    project = Repo(repo, branch)
    project_commits = project.commits()

    in_build = [c for c in project_commits if c['sha'] in commits]

    for s in in_build:
        print(u'commit {}'.format(s['sha']))
        print(u'')
        for l in s['message'].split('\n'):
            print(u'\t{}'.format(l))
        print(u'')


@cli.command()
@click.option("--repo")
@click.option("--branch")
def latest_build(repo, branch):
    git_sha = get_latest_build(branch)
    git_sha = '3678754'

    enterprise_dist = EnterpriseDist()
    vanagon_git_ref = enterprise_dist.get_vanagon_commit_sha(git_sha)

    vanagon = PeModulesVanagon(branch)
    repo_git_ref = vanagon.get_repo_commit_sha(vanagon_git_ref, repo)

    project = Repo(repo, branch)
    project_commit = project.latest()

    if project_commit['sha'] == repo_git_ref:
        print(project_commit['message'])
    else:
        print('Project was not tested in the latest smoke test')


if __name__ == '__main__':
    cli()
