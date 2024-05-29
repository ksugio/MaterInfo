from django.core.management.base import BaseCommand, CommandError
from image.models.size import Size

class Command(BaseCommand):
    help = "Measure size if results not exsist"

    def handle(self, *args, **options):
        for size in Size.objects.all():
            if not size.results:
                self.stdout.write('%d %s measuring' % (size.id, size.title), ending="\n")
                size.measure()
                size.save()
