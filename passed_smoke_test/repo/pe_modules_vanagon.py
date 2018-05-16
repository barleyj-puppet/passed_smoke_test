from base import Repo
from passed_smoke_test.log import Logger, logger_group


log = Logger(__name__)
logger_group.add_logger(log)


class PeModulesVanagon(Repo):
    name = 'pe-modules-vanagon'
    
    def __init__(self, branch):
        log.debug('Branch: {}'.format(branch))
        Repo.__init__(self, self.name, branch)

        
    def get_repo_commit_sha(self, git_sha, repo):
        commit = self.commit(git_sha)
        if commit:
            message = commit['message']
            log.debug('Commit message: {}'.format(message.rstrip()))

        
            if repo in message:
                repo_git_ref = message.strip().split(' ')[6]

                return repo_git_ref
