from django.core.management.base import BaseCommand, CommandError
from project.models import Prefix, UniqueID
from general.models import General
from material.models import Material
from density.models import Density
from hardness.models import Hardness
from value.models.aggregate import Aggregate
from value.models.curve import Curve
from image.models.size import Size
from image.models.ln2d import LN2D
from image.models.imfp import IMFP

class Command(BaseCommand):
    help = "Set unique id to prefix and change features"

    def add_arguments(self, parser):
        parser.add_argument('--unique', action='store_true', dest='set-unique',
                            help='set unique id to prefix, run first')

    def change(self, item):
        if len(item.prefix) < 6:
            prefix = Prefix.objects.filter(id=int(item.prefix))
            if prefix:
                item.prefix = prefix[0].unique
                item.save()
                self.stdout.write('%s %d %s %s' % (item.__class__.__name__, item.id, item.title, item.prefix), ending="\n")

    def handle(self, *args, **options):
        if options['set-unique']:
            for prefix in Prefix.objects.all():
                prefix.unique = UniqueID()
                prefix.save()
                self.stdout.write('Prefix %d %s %s' % (prefix.id, prefix.prefix, prefix.unique), ending="\n")
        else:
            for item in General.objects.all():
                self.change(item)
            for item in Material.objects.all():
                self.change(item)
            for item in Density.objects.all():
                self.change(item)
            for item in Aggregate.objects.all():
                self.change(item)
            for item in Curve.objects.all():
                self.change(item)
            for item in Size.objects.all():
                self.change(item)
            for item in LN2D.objects.all():
                self.change(item)
            for item in IMFP.objects.all():
                self.change(item)
