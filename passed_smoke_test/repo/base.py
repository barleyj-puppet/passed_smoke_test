import git

from passed_smoke_test.releases import releases

remote_name = 'puppet'


def _to_hash(commit):
    return {
        'sha': commit.hexsha,
        'date': commit.authored_date,
        'message': commit.message,
    }


class Repo:
    organization = 'git@github.com:puppetlabs'

    def __init__(self, project, named_branch=None):
        """Initializes, clones and checks out a branch if specified"""
        
        repo = git.Repo.init('/tmp/{}'.format(project))

        for remote in repo.remotes:
            if remote.name == remote_name:
                break
        else:
            repo.create_remote(remote_name, url='{}/{}.git'.format(self.organization, project))

        remote = repo.remotes[remote_name]
        fetch = remote.fetch()

        if named_branch:
            # This is because we've changed some modules to use a name instead of a version
            branch = releases[project][named_branch]
            repo.create_head(branch, remote.refs[branch]).set_tracking_branch(remote.refs[branch]).checkout()

        self.repo = repo


    def commits(self):
        commits = [_to_hash(c) for c in self.repo.iter_commits()]

        return commits

    
    def commit(self, sha):
        commit = self.repo.commit(sha)

        return _to_hash(commit)


    def latest(self):
        commit = list(self.repo.iter_commits())[0]

        return _to_hash(commit)
