import git
from gitdb.exc import BadName

import pandas

from passed_smoke_test.log import Logger, logger_group
from passed_smoke_test.releases import releases


log = Logger(__name__)
logger_group.add_logger(log)

remote_name = 'puppet'


def _to_map(commit):
    return {
        'sha': commit.hexsha,
        'date': pandas.to_datetime(commit.authored_date, unit='s'),
        'message': commit.message,
    }


class Repo:
    organization = 'git@github.com:puppetlabs'

    def __init__(self, project, named_branch):
        """Initializes, clones and checks out a branch if specified"""

        # This is because we've changed some modules to use a name instead of a version
        self.name = project
        branch = releases[project][named_branch]
        repo = git.Repo.init('/tmp/{}'.format(project))

        for remote in repo.remotes:
            if remote.name == remote_name:
                break
        else:
            repo.create_remote(remote_name, url='{}/{}.git'.format(self.organization, project))

        remote = repo.remotes[remote_name]

        if named_branch:
            remote.fetch()

            log.debug('Active branch: {}'.format(repo.active_branch.name))
            if branch not in repo.heads:
                repo.create_head(branch, remote.refs[branch])
                
            if repo.active_branch.name != branch:
                head = repo.heads[branch]
                head.set_tracking_branch(remote.refs[branch])
                head.checkout()

            log.debug('Pulling branch {} in repo {}.'.format(branch, project))
            remote.pull('--rebase')
        
        self.repo = repo


    def commits(self):
        commits = [_to_map(c) for c in self.repo.iter_commits()]

        return commits

    
    def commit(self, sha):
        log.debug('Git SHA: {}'.format(sha))
        if sha:
            try:
                commit = self.repo.commit(sha)
                return _to_map(commit)
            except BadName:
                log.debug('Commit {} was not found in {}.'.format(sha, self.name))
                return None
            

    def latest(self):
        commit = list(self.repo.iter_commits())[0]

        return _to_map(commit)
