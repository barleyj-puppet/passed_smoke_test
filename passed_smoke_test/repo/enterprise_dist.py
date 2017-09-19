from base import Repo


class EnterpriseDist(Repo):
    name = 'enterprise-dist'
    
    def __init__(self):
        Repo.__init__(self, self.name)
        

    def get_vanagon_commit_sha(self, git_sha):
        commit = self.commit(git_sha)
        message = commit['message']
        vanagon_git_ref = message.split()[-1]

        return vanagon_git_ref
