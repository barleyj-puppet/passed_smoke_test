from github import Github

from passed_smoke_test.log import Logger, logger_group

log = Logger(__name__)
logger_group.add_logger(log)


class PullRequest:
    def __init__(self, repo, id, username, token):
        "Initilizes PR from Github"
        g = Github(username, token)
        org = g.get_organization('puppetlabs')
        self._pr = org.get_repo(repo).get_pull(id)
        self.number = id
        self.repo = self._pr.base.repo
        
    @property
    def is_merged(self):
        pr = self._pr
        log.debug('PR State: {}'.format(pr.state))
        return pr.state in ('declined', 'closed')

        
    
    @property
    def commits(self):
        commits = [c.sha for c in self._pr.get_commits()]
        commits.insert(0, self._pr.merge_commit_sha)
        log.debug('Commit Data: {}'.format(commits))
        return commits
