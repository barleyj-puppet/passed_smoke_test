from base import Repo
from passed_smoke_test.log import Logger, logger_group
from passed_smoke_test.releases import releases


log = Logger(__name__)
logger_group.add_logger(log)


class EnterpriseDist(Repo):
    name = 'enterprise-dist'
    
    def __init__(self, branch):
        Repo.__init__(self, self.name, branch)
        

    def get_vanagon_commit_sha(self, git_sha):
        commit = self.commit(git_sha)
        message = commit['message']

        log.debug('Enterprise Dist commit message: {}'.format(message.rstrip()))
        if 'pe-modules' in message:
            vanagon_git_ref = message.split()[-1]

            return vanagon_git_ref
