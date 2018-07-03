#!/usr/bin/env python
import json
import os
import pprint
import re
import sys

import click
import pandas

from automation import Jenkins
from log import Logger, logger_group, DEBUG
from repo import Repo, EnterpriseDist, PeModulesVanagon
from releases import releases
from ticket import PullRequest, Ticket, Project


log = Logger(__name__)
logger_group.add_logger(log)

def parse_build_description(description):
    log.debug('Build Description: {}'.format(description))
    parts = description.split('-')

    return parts[3][1:] if len(parts) == 4 else None


def extract_repo_commit(message):
    m = re.match('Update for (.*) \((.*)\), GIT REF (.*)\n.*', message)
    items = []
    if m:
        items = list(m.groups())

    return pandas.Series(items)


def join(enterprise_dist, vanagon_commits, build_numbers, promotion_build_numbers, pull_requests):
    enterprise_dist = pandas.merge(enterprise_dist, vanagon_commits, how='outer', left_on='git_ref', right_on='sha', suffixes=('_ed', '_v'))
    enterprise_dist = pandas.merge(enterprise_dist, build_numbers, how='outer', left_on='short_sha', right_on='commit', suffixes=('_ed', '_bn'))
    enterprise_dist = pandas.merge(enterprise_dist, promotion_build_numbers, how='outer', left_on='commit', right_on='commit', suffixes=('_bn', '_pbn'))
    enterprise_dist = pandas.merge(enterprise_dist, pull_requests, how='outer', left_on='git_ref_v', right_on='commit', suffixes=('_v', '_pr'))

    return enterprise_dist


@click.group()
@click.option('--debug', is_flag=True)
def cli(debug):
    if debug:
        logger_group.level = DEBUG


@cli.command()
@click.option('--branch', required=True)
@click.option("--ticket", required=True)
@click.option("--jira-username", envvar='JIRA_USERNAME', required=True, help='Can be provided by setting the JIRA_USERNAME environment variable.')
@click.option("--jira-token", prompt=True, hide_input=True, envvar='JIRA_TOKEN', required=True, help='Can be provided by setting the JIRA_TOKEN environment variable. Will prompt if this option is not provided.')
@click.option("--jenkins-username", envvar='JENKINS_USERNAME', required=True, help='Can be provided by setting the JENKINS_USERNAME environment variable.')
@click.option("--jenkins-token", prompt=True, hide_input=True, envvar='JENKINS_TOKEN', required=True, help='Can be provided by setting the JENKINS_TOKEN environment variable. Will prompt if this option is not provided.')
@click.option("--github-username", envvar='GITHUB_USERNAME', required=True, help='Can be provided by setting the GITHUB_USERNAME environment variable.')
@click.option("--github-token", prompt=True, hide_input=True, envvar='GITHUB_TOKEN', required=True, help='Can be provided by setting the GITHUB_TOKEN environment variable. Will prompt if this option is not provided.')
@click.option("--force", is_flag=True)
def ticket(branch, ticket, jira_username, jira_token, jenkins_username, jenkins_token, github_username, github_token, force):
    "Tells you if a ticket has passed smoke test and has been promoted into a build"

    default_branch = releases['default'][branch]
    issue = Ticket(ticket, branch, jira_username, jira_token, github_username, github_token)
    project = Project(jira_username, jira_token)
    log.debug('Ticket ID: {}'.format(issue.id))
    server = Jenkins(jenkins_username, jenkins_token)
    enterprise_dist = EnterpriseDist(branch)
    vanagon = PeModulesVanagon(branch)

    # Parse PR's into format DataFrame can be created from
    # First PR commit is the merge commit
    pr_commits = [{'pr': str(pr), 'pr_number': pr.number, 'repo': pr.repo.name, 'commit': pr.commits[0], 'is_merged': pr.is_merged} for pr in issue.pull_requests]
    pull_requests = pandas.DataFrame(pr_commits, columns=['pr', 'pr_number', 'repo', 'commit', 'is_merged'])
    if not pull_requests['is_merged'].all():
        click.echo("Not all PR's for this ticket have been merged")
        exit(1)

    # Build numbers that have passed smoke tests and the Enterprise Dist commit
    build_numbers = pandas.DataFrame(server.smoke_tests(default_branch), columns=['build_number'])
    build_numbers['commit'] = build_numbers['build_number'].apply(parse_build_description)

    # Build numbers that were promoted and the Enterprise Dist commit
    promotion_build_numbers = pandas.DataFrame(server.promotions(default_branch), columns=['build_number'])
    promotion_build_numbers['commit'] = promotion_build_numbers['build_number'].apply(parse_build_description)

    # Enterprise Dist commits
    # short_sha corresponds to build number commits. Doing this instead of
    # doing a merge based on starts with.
    enterprise_dist = pandas.DataFrame(enterprise_dist.commits())
    enterprise_dist['date'] = pandas.to_datetime(enterprise_dist['date'])
    enterprise_dist[['repo', 'rc', 'git_ref']] = enterprise_dist['message'].apply(extract_repo_commit)
    enterprise_dist['short_sha'] = enterprise_dist['sha'].apply(lambda s: s[0:7])

    # Vanagon commits
    vanagon_commits = pandas.DataFrame(vanagon.commits())
    vanagon_commits[['repo', 'rc', 'git_ref']] = vanagon_commits['message'].apply(extract_repo_commit)

    # Join all data together
    enterprise_dist = join(enterprise_dist, vanagon_commits, build_numbers, promotion_build_numbers, pull_requests)

    # Filter for commits that have a matching PR
    pr_rows = enterprise_dist[enterprise_dist['commit_pr'].notnull()]

    if not pr_rows.empty and (force or pr_rows['build_number_pbn'].notnull().all()):
        passed_smoke_bn = pr_rows['build_number_bn'].iloc[0]
        passed_smoke_message = 'Ticket {} passed smoke test in build {}'.format(ticket, passed_smoke_bn)
        click.echo(passed_smoke_message)

        promoted_bn = pr_rows['build_number_pbn'].iloc[0]
        promoted_message = 'Ticket {} was promoted in build {}'.format(ticket, promoted_bn)
        click.echo(promoted_message)

    else:
        click.echo("Unable to find builds for all PR's in this ticket")
        exit(1)

    if click.confirm('Do you wish to update ticket {}?'.format(ticket)):
        if not issue.fix_build:
            issue.fix_build = promoted_bn

        versions = project.fix_versions
        version_choices = ['{}. {}'.format(x+1, v['name']) for x, v in enumerate(versions)]
        click.echo('\n'.join(version_choices))
        fix_version = click.prompt('Please choose which version this change is targetting', type=int)
        click.echo('You chose: {}'.format(versions[fix_version-1]))
        issue.fix_versions = versions[fix_version-1]
        issue.comment('\n'.join([passed_smoke_message, promoted_message]))
        click.echo('Comment added')


@cli.command()
@click.option("--repo")
@click.option("--branch")
@click.option("--jenkins-username", envvar='JENKINS_USERNAME', required=True, help='Can be provided by setting the JENKINS_USERNAME environment variable.')
@click.option("--jenkins-token", prompt=True, hide_input=True, envvar='JENKINS_TOKEN', required=True, help='Can be provided by setting the JENKINS_TOKEN environment variable. Will prompt if this option is not provided.')
def last_build(repo, branch, jenkins_username, jenkins_token):
    "Outputs the last commit of a repo if one of the current smoke tests ran on that commit"

    default_branch = releases['default'][branch]
    server = Jenkins(jenkins_username, jenkins_token)
    enterprise_dist = EnterpriseDist(branch)
    vanagon = PeModulesVanagon(branch)

    build_numbers = server.smoke_tests(default_branch)

    for build in build_numbers:
        sha = parse_build_description(build)
        vanagon_ref = enterprise_dist.get_vanagon_commit_sha(sha)
        repo_ref = vanagon.get_repo_commit_sha(vanagon_ref, repo)
        if repo_ref:
            click.echo('Commit {} in repo {} passed smoke test in build {}'.format(repo_ref, repo, build))
            break


@cli.command()
@click.option("--repo")
@click.option("--branch")
def missing(repo, branch):
    "DO NOT USE - Show commits in repo that have not made it into pe-modules-vanagon"

    vanagon = PeModulesVanagon(branch)
    commits = vanagon.commits(repo)

    project = Repo(repo, branch)
    project_commits = project.commits()

    in_build = [c for c in project_commits if c['sha'] not in commits]

    for s in in_build:
        click.echo(u'commit {}'.format(s['sha']))
        click.echo(u'')
        for l in s['message'].split('\n'):
            click.echo(u'\t{}'.format(l))
        click.echo(u'')


@cli.command()
@click.option("--repo")
@click.option("--branch")
def commits(repo, branch):
    "Outputs all commits in repo that are in pe-modules-vanagon"

    vanagon = PeModulesVanagon(branch)
    commits = vanagon.commits()

    project = Repo(repo, branch)
    project_commits = project.commits()

    in_build = [c for c in project_commits for v in commits if repo in v['message'] and c['sha'] in v['message']]

    for s in in_build:
        commit = 'commit: {}'.format(s['sha'])
        output = [commit]
        output.extend(s['message'].split('\n'))
        click.echo('\n\t'.join(output))


@cli.command()
@click.option("--repo")
@click.option("--branch")
@click.option("--jenkins-username", envvar='JENKINS_USERNAME', required=True, help='Can be provided by setting the JENKINS_USERNAME environment variable.')
@click.option("--jenkins-token", prompt=True, hide_input=True, envvar='JENKINS_TOKEN', required=True, help='Can be provided by setting the JENKINS_TOKEN environment variable. Will prompt if this option is not provided.')
def latest_build(repo, branch, jenkins_username, jenkins_token):
    "Outputs the commit message for the last commit in the repo's branch"

    default_branch = releases['default'][branch]
    server = Jenkins(jenkins_username, jenkins_token)
    enterprise_dist = EnterpriseDist(branch)
    vanagon = PeModulesVanagon(branch)

    last_build = server.last_build(default_branch)
    sha = parse_build_description(last_build)

    vanagon_ref = enterprise_dist.get_vanagon_commit_sha(sha)
    repo_ref = vanagon.get_repo_commit_sha(vanagon_ref, repo)

    project = Repo(repo, branch)
    project_commit = project.latest()

    if project_commit['sha'] == repo_ref:
        click.echo(project_commit['message'])
    else:
        click.echo('Project was not tested in the latest smoke test')


if __name__ == '__main__':
    cli()
