from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string
from config.settings import COLLECT_FILTER_PROCESS
from collect.models.process import Process

class Command(BaseCommand):
    help = "Register process name"

    def searchname(self, id):
        for item in COLLECT_FILTER_PROCESS:
            cls = import_string(item['Model'])
            obj = cls.objects.filter(id=id)
            if obj:
                return obj[0].__class__.__name__

    def handle(self, *args, **options):
        processes = Process.objects.all()
        for proc in processes:
            if not proc.name:
                name = self.searchname(proc.id)
                self.stdout.write(str(proc.id) + ' ' + name, ending="\n")
                proc.name = name
                proc.save()
