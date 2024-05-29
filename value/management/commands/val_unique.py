from django.core.management.base import BaseCommand, CommandError
from project.models import UniqueStr
from value.models.value import Value
from value.models.filter import Filter

class Command(BaseCommand):
    help = "Set unique id"

    def set_unique_id(self, items):
        for item in items:
            item.unique = UniqueStr()
            item.save()
            self.stdout.write('%s %d %s' % (item.__class__.__name__, item.id, item.unique), ending="\n")

    def handle(self, *args, **options):
        self.set_unique_id(Value.objects.all())
        self.set_unique_id(Filter.objects.all())
