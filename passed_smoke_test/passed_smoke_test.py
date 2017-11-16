#!/usr/bin/env python
import json
import os
import pprint
import sys

import click

from automation import Jenkins
from log import Logger, logger_group, DEBUG
from repo import Repo, EnterpriseDist, PeModulesVanagon
from releases import releases
from ticket import PullRequest, Ticket


log = Logger(__name__)
logger_group.add_logger(log)

def parse_build_description(description):
    log.debug('Build Description: {}'.format(description))
    parts = description.split('-')

    return parts[3][1:] if len(parts) == 4 else None


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
def ticket(branch, ticket, jira_username, jira_token, jenkins_username, jenkins_token, github_username, github_token):
    "Tells you if a ticket has passed smoke test and has been promoted into a build"

    default_branch = releases['default'][branch]
    issue = Ticket(ticket, branch, jira_username, jira_token, github_username, github_token)
    log.debug('Ticket ID: {}'.format(issue.id))

    if issue.is_merged:
        server = Jenkins(jenkins_username, jenkins_token)

        build_numbers = server.smoke_tests(default_branch)

        promotion_build_numbers = server.promotions(default_branch)

        shas = filter(lambda x: x, map(parse_build_description, build_numbers))
        enterprise_dist = EnterpriseDist(branch)
        vanagon = PeModulesVanagon(branch)

        vanagon_shas = [enterprise_dist.get_vanagon_commit_sha(sha) for sha in shas]

        data = {}
        for pr in issue.pull_requests:
            click.echo('Checking PR: {}'.format(pr.number))
            log.debug('Repo: {}, Pull Request: {}'.format(pr.repo.name, int(pr.number)))
            repo_shas = [vanagon.get_repo_commit_sha(vanagon_ref, pr.repo.name) for vanagon_ref in vanagon_shas]
            for commit in pr.commits:
                click.echo('Checking that commit {} passed smoke test in pe-modules-vanagon'.format(commit))
                log.debug('PR Commit: {}'.format(commit))
                if commit and commit in repo_shas:
                    i = repo_shas.index(commit)
                    log.debug('Build Number: {}'.format(build_numbers[i]))
                    log.debug('Repository {} has commit {}'.format(pr.repo.name, commit))
                    log.debug('Ticket {} passed smoke test in build {}'.format(ticket, build_numbers[i]))
                    data[build_numbers[i]] = {'smoke': pr.repo.name}
                    click.echo('Checking that commit {} was promoted'.format(commit))
                    if build_numbers[i] in promotion_build_numbers:
                        log.debug('Ticket {} was promoted in build {}'.format(ticket, build_numbers[i]))
                        data[build_numbers[i]]['promoted'] = pr.repo.name

        if data:
            messages = []
            build = sorted(data.keys(), reverse=True)[0]
            build_message = 'Ticket {} passed smoke test in build {}'.format(ticket, build)
            click.echo(build_message)
            messages.append(build_message)
            if 'promoted' in data[build]:
                promoted_message = 'Ticket {} was promoted in build {}'.format(ticket, build)
                click.echo(promoted_message)
                messages.append(promoted_message)
            if click.confirm('Do you wish to add this comment to ticket {}'.format(ticket)):
                issue.comment('\n'.join(messages))
                click.echo('Comment added')
        else:
            click.echo('Unable to find this {} in a build of enterprise-dist that passed smoke test or was promoted.'.format(ticket))
    else:
        click.echo("Not all PR's for this ticket have been merged")


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
    commits = vanagon.commits(repo)

    project = Repo(repo, branch)
    project_commits = project.commits()

    in_build = [c for c in project_commits if c['sha'] in commits]

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
