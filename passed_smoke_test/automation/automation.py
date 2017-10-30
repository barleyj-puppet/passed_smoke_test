import jenkins as _jenkins

from passed_smoke_test.log import Logger, logger_group


log = Logger(__name__)
logger_group.add_logger(log)


class Jenkins:
    def __init__(self, jenkins_username, jenkins_token):
        "Creates connection to Jenkins server"
        self.server = _jenkins.Jenkins('https://cinext-jenkinsmaster-enterprise-prod-1.delivery.puppetlabs.net', username=jenkins_username, password=jenkins_token)

    def last_build(self, branch):
        "Returns the last completed build"

        job_name = 'enterprise_pe-acceptance-tests_integration-system_pe_smoke-upgrade_{}'.format(branch)
        build_info = self._builds(job_name)[0]
        build_description = build_info['description']

        return build_description

    def smoke_tests(self, branch):
        "Returns all build numbers that have passed smoke test"
        
        job_name = 'enterprise_pe-acceptance-tests_integration-system_pe_smoke-upgrade_{}'.format(branch)
        builds = self._builds(job_name)
        build_numbers = [b['description'] for b in builds if b['result']  == 'SUCCESS']

        return build_numbers

    def promotions(self, branch):
        "Returns all build numbers that have been promoted"
        
        job_name = 'enterprise_pe-acceptance-tests_packaging_promotion_{}'.format(branch)
        builds = self._builds(job_name)
        build_numbers = [parameter['value']
                         for b in builds
                         for parameter in b['actions'][0]['parameters']
                         if b['result']  == 'SUCCESS' and parameter['name'] == 'pe_version']

        return build_numbers

    def _builds(self, job_name):
        "Retrieves all builds for a job"
        
        server = self.server
        info = server.get_job_info(job_name)
        builds = [server.get_build_info(job_name, build['number']) for build in info['builds']]

        return builds
