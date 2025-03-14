from django.core.management.base import BaseCommand, CommandError
from accounts.models import CustomUser
from project.views.token import ParseURL, Login
from project.views.project import ProjectRemote
from getpass import getpass

class Command(BaseCommand):
    help = "Clone project"
    view_name = "project:detail"
    view_args = 1
    remote_class = ProjectRemote

    def add_arguments(self, parser):
        parser.add_argument('--url', nargs='?', default='', type=str)
        parser.add_argument('--user', nargs='?', default='', type=str)

    def handle(self, *args, **options):
        if not options['user']:
            localname = input("Local Username: ")
        else:
            localname = options['user']
        localuser = CustomUser.objects.filter(username=localname)
        if not localuser:
            raise CommandError("Invalid Username")
        if not options['url']:
            url = input("Url: ")
        else:
            url = options['url']
        username = input("Remote Username: ")
        password = getpass("Remote Password: ")
        rooturl, id, _ = ParseURL(url, self.view_name, self.view_args)
        refresh, access = Login(rooturl, username, password)
        if refresh:
            self.clone(rooturl, id, access, localuser[0])
        else:
            raise CommandError("Invalid Username or Password")

    def clone(self, rooturl, id, access, localuser):
        remote = self.remote_class()
        option = {
            'rooturl': rooturl,
            'access': access,
            'scan_lower': True
        }
        clone_list = remote.clone_list(id, **option)
        if clone_list is not None:
            option = {
                'rooturl': rooturl,
                'access': access,
                'root_remoteid': id,
                'scan_lower': True,
                'set_remote': True
            }
            kwargs, objects = remote.clone_exec(clone_list, None, localuser, **option)
