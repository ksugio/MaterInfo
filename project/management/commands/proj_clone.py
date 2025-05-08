from django.core.management.base import BaseCommand, CommandError
from accounts.models import CustomUser
from project.models import Project
from project.views.requests import ParseURL, Login
from project.views.project import ProjectRemote
from project.tasks import CloneTask, PullTask, PushTask
from getpass import getpass

class Command(BaseCommand):
    help = "Clone project"
    view_name = "project:detail"
    view_args = 1
    model = Project
    remote_class = ProjectRemote
    remote_name = 'project.views.project.ProjectRemote'

    def add_arguments(self, parser):
        parser.add_argument('--pull', action='store_true', dest='pull-exec',
                            help='excute pull')
        parser.add_argument('--push', action='store_true', dest='push-exec',
                            help='excute push')

    def handle(self, *args, **options):
        localname = input("Local Username: ")
        localuser = CustomUser.objects.filter(username=localname)
        if not localuser:
            raise CommandError("Invalid Username")
        if options['pull-exec']:
            self.pull(localuser[0])
        elif options['push-exec']:
            self.push(localuser[0])
        else:
            self.clone(localuser[0])

    def clone(self, localuser):
        url = input("Url: ")
        username = input("Remote Username: ")
        password = getpass("Remote Password: ")
        rooturl, id, _ = ParseURL(url, self.view_name, self.view_args)
        refresh, access = Login(rooturl, username, password)
        if not refresh:
            raise CommandError("Invalid Username or Password")
        CloneTask(self.remote_name, rooturl, id, access, 'JWT', url,
                  None, True, True,
                  '', 0, request_user_id=localuser.id)

    def pull(self, localuser):
        id = input("Local ID: ")
        models = self.model.objects.filter(pk=id)
        if not models:
            raise CommandError("Invalid ID")
        model = models[0]
        username = input("Remote Username: ")
        password = getpass("Remote Password: ")
        refresh, access = Login(model.remoteurl, username, password)
        if not refresh:
            raise CommandError("Invalid Username or Password")
        PullTask(self.remote_name, id, access, None,
                 request_user_id=localuser.id)

    def push(self, localuser):
        id = input("Local ID: ")
        models = self.model.objects.filter(pk=id)
        if not models:
            raise CommandError("Invalid ID")
        model = models[0]
        username = input("Remote Username: ")
        password = getpass("Remote Password: ")
        refresh, access = Login(model.remoteurl, username, password)
        if not refresh:
            raise CommandError("Invalid Username or Password")
        PushTask(self.remote_name, id, access, None,
                       request_user_id=localuser.id)
