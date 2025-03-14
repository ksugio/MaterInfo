from django.core.management.base import BaseCommand, CommandError
from image.models.filter import Filter

class Command(BaseCommand):
    help = "Save filter file if file not exsist"

    def handle(self, *args, **options):
        for filter in Filter.objects.all():
            if not filter.file:
                self.stdout.write('%d %s saving' % (filter.id, filter.title), ending="\n")
                filter.savefile()
                filter.save()
