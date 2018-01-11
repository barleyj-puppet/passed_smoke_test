import json
import pprint

from jira import JIRA

from .pull_request import PullRequest
from passed_smoke_test.log import Logger, logger_group
from passed_smoke_test.releases import releases


log = Logger(__name__)
logger_group.add_logger(log)

PULL_REQUEST = 'https://tickets.puppetlabs.com/rest/dev-status/latest/issue/detail?issueId={}&applicationType=github&dataType=pullrequest'
REPOSITORY   = 'https://tickets.puppetlabs.com/rest/dev-status/latest/issue/detail?issueId={}&applicationType=github&dataType=repository'
    
MERGING     = '10002'
INTEGRATING = '10003'


def destination(url):
    return url.split('/')[4]


def id(id):
    return int(id[1:])


class Ticket(object):
    def __init__(self, issue_id, branch, username, password, github_username, github_token):
        options = {
            'server': 'https://tickets.puppetlabs.com'}

        self.github_username = github_username
        self.github_token = github_token
        
        jira_client = JIRA(options, basic_auth=(username, password))
        self.jira_client = jira_client
        self.session = jira_client._session.get

        self.issue = jira_client.issue(issue_id)
        self.id = self.issue.id
        self.branch = branch

    @property
    def pull_requests(self):
        branch = self.branch
        req_url =  PULL_REQUEST.format(self.id)
        response = self.session(req_url)
        raw_data = json.loads(response.content)
        log.debug('PR Data: {}'.format(pprint.pformat(raw_data)))
        jira_pull_requests = [pr for pr in raw_data['detail'][0]['pullRequests']
                              if pr['destination']['branch'] == releases[destination(pr['destination']['url'])][branch]
                              and pr['status'] != 'DECLINED']
        log.debug('JIRA Pull Requests: {}'.format(pprint.pformat(jira_pull_requests)))
        # Trim leading # from id
        pull_requests = [PullRequest(destination(pr['destination']['url']), id(pr['id']), self.github_username, self.github_token)
                         for pr in jira_pull_requests]
        log.debug('Pull Requests: {}'.format(pull_requests))
        return pull_requests

    @property
    def is_merged(self):
        return all(pr.is_merged for pr in self.pull_requests)


    def comment(self, message):
        comment = self.jira_client.add_comment(self.issue, 'new comment')
        comment.update(body = message)
