from django.core.management.base import BaseCommand
from project.models import UniqueStr
from image.models.image import Image
from image.models.filter import Filter
from image.models.size import Size
from image.models.ln2d import LN2D
from image.models.imfp import IMFP

class Command(BaseCommand):
    help = "Set unique id"

    def set_unique_id(self, items):
        for item in items:
            item.unique = UniqueStr()
            item.save()
            self.stdout.write('%s %d %s' % (item.__class__.__name__, item.id, item.unique), ending="\n")

    def handle(self, *args, **options):
        self.set_unique_id(Image.objects.all())
        self.set_unique_id(Filter.objects.all())
        self.set_unique_id(Size.objects.all())
        self.set_unique_id(LN2D.objects.all())
        self.set_unique_id(IMFP.objects.all())
