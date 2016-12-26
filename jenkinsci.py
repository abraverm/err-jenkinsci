import requests
from errbot import botcmd, BotPlugin
from jenkinsapi.jenkins import Jenkins

class MissingConfiguration(Exception):
    pass

class JenkinsCiBot(BotPlugin):
    version = '0.1-devel'
    name = 'jenkins-ci-plugin'

    def get_configuration_template(self):
        return {
            'url': None,
            'username': None,
            'password': None,
            'ssl_verify': True,
        }

    @botcmd
    def jenkins_version(self, msg, args):
        """Print jenkins ci version"""
        return "%s %s" % (self.name, self.version)

    @botcmd
    def jenkins_info(self, msg, args):
        """Print information about jenkins"""
        c = self.client()
        return "jenkins url='%s' version='%s' user='%s'" % (c.baseurl, c.version, c.username)

    @botcmd
    def jenkins_jobs(self, msg, args):
        """Print all jobs"""
        c = self.client()
        return '\n'.join(c.get_jobs_list())

    @botcmd
    def jenkins_statjob(self, msg, args):
        if len(args) < 1:
            return "Missing jobs. To see jobs run '!jenkins jobs'"
        c = self.client()
        res = []
        for job in args.split(' '):
            build = c[job].get_last_build()
            number = build.get_number()
            status = build.get_status()
            res.append('%s #%s is %s' % (job, number, status))
        return '\n'.join(res)

    @botcmd
    def jenkins_console(self, msg, args):
        if len(args) < 1:
            return "Missing job name. To see jobs run '!jenkins jobs'"
        c = self.client()
        if args not in c:
            return "{0} is not a jenkins job. Run '!jenkins jobs'".format(args)
        build = c[args].get_last_build()
        no = str(build.get_number())
        console_url = '/'.join([c.baseurl, 'job', args, no, 'console'])
        return 'console: %s' % console_url

    @botcmd
    def jenkins_start(self, msg, args):
        if len(args) < 1:
            return "Missing job name. To see jobs run '!jenkins jobs'"
        c = self.client()
        if args not in c:
            return "{0} is not a jenkins job. Run '!jenkins jobs'".format(args)
        resp = requests.get(c[job].get_build_triggerurl())
        if resp.status_code == 200:
            return 'start job'
        return 'failed starting job: status code %s' % resp.status_code

    @botcmd
    def jenkins_stop(self, msg, args):
        if len(args) < 1:
            return "Missing job name. To see jobs run '!jenkins jobs'"
        c = self.client()
        if args not in c:
            retrun "{0} is not a jenkins job. Run '!jenkins jobs'".format(args)
        res = c.get_last_build().stop()
        if res:
            return "Job is stopped already"
        return "Job just got stopped!"

    def client(self):
        if self.config['url'] is None:
            raise MissingConfiguration("'url' is missing")
        return Jenkins(self.config['url'],
                       username=self.config['username'],
                       password=self.config['password'],
                       ssl_verify=self.config['ssl_verify'])
