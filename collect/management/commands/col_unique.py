from collect.models.clustering import Clustering
from django.core.management.base import BaseCommand, CommandError
from project.models import UniqueStr
from collect.models.collect import Collect
from collect.models.filter import Filter
from collect.models.reduction import Reduction
from collect.models.classification import Classification

class Command(BaseCommand):
    help = "Set unique id"

    def set_unique_id(self, items):
        for item in items:
            item.unique = UniqueStr()
            item.save()
            self.stdout.write('%s %d %s' % (item.__class__.__name__, item.id, item.unique), ending="\n")

    def handle(self, *args, **options):
        self.set_unique_id(Collect.objects.all())
        self.set_unique_id(Filter.objects.all())
        self.set_unique_id(Reduction.objects.all())
        self.set_unique_id(Clustering.objects.all())
        self.set_unique_id(Classification.objects.all())
