import json
import pprint

from jira import JIRA

from passed_smoke_test.log import Logger, logger_group


FIX_VERSIONS = 'https://tickets.puppetlabs.com/rest/api/latest/project/PE/versions'


class Project(object):
    def __init__(self, username, password):
        options = {
            'server': 'https://tickets.puppetlabs.com'}

        jira_client = JIRA(options, basic_auth=(username, password))
        self.jira_client = jira_client
        self.session = jira_client._session.get

    @property
    def fix_versions(self):
        response = self.session(FIX_VERSIONS)
        raw_data = json.loads(response.content)
        return [{'id': v['id'], 'name': v['name']} for v in raw_data if not v['archived'] and not v['released']]
