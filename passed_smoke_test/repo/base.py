import git
from gitdb.exc import BadName

from passed_smoke_test.log import Logger, logger_group
from passed_smoke_test.releases import releases


log = Logger(__name__)
logger_group.add_logger(log)

remote_name = 'puppet'


def _to_map(commit):
    return {
        'sha': commit.hexsha,
        'date': commit.authored_date,
        'message': commit.message,
    }


class Repo:
    organization = 'git@github.com:puppetlabs'

    def __init__(self, project, named_branch):
        """Initializes, clones and checks out a branch if specified"""

        # This is because we've changed some modules to use a name instead of a version
        branch = releases[project][named_branch]

        repo = git.Repo.init('/tmp/{}'.format(project))

        for remote in repo.remotes:
            if remote.name == remote_name:
                break
        else:
            repo.create_remote(remote_name, url='{}/{}.git'.format(self.organization, project))

        remote = repo.remotes[remote_name]

        if named_branch:
            remote.fetch(branch)

            log.debug('Active branch: {}'.format(repo.active_branch.name))
            if repo.active_branch.name != branch:
                if branch in repo.heads:
                    repo.delete_head(branch)

                repo.create_head(branch, remote.refs[branch]).set_tracking_branch(remote.refs[branch]).checkout()

            log.debug('Pulling branch {} in repo {}.'.format(branch, project))
            remote.pull(branch, rebase=True)
        
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
                log.debug('Commit {} was not found in {}.'.format(sha, self.repo.name))
                return None
            

    def latest(self):
        commit = list(self.repo.iter_commits())[0]

        return _to_map(commit)
