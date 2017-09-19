from base import Repo


class PeModulesVanagon(Repo):
    name = 'pe-modules-vanagon'
    
    def __init__(self, branch):
        Repo.__init__(self, self.name, branch)
        

    def get_repo_commit_sha(self, git_sha, repo):
        commit = self.commit(git_sha)
        message = commit['message']
        repo_git_ref = message.strip().split(' ')[6]

        return repo_git_ref


    def commits(self, repo):
        commits = {c.message.strip().split(' ')[6] for c in self.repo.iter_commits() if 'GIT REF' in c.message and repo in c.message}

        return commits

        
