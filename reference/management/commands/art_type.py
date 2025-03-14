from django.core.management.base import BaseCommand
from reference.models.article import Article

class Command(BaseCommand):
    help = "Change article type initial to Bibtex"

    def handle(self, *args, **options):
        articles = Article.objects.all()
        for art in articles:
            if art.type == 1:
                art.type = 5
                art.save()
                self.stdout.write(str(art.id) + ' Changed 1 to 5', ending="\n")
            elif art.type == 3:
                art.type = 1
                art.save()
                self.stdout.write(str(art.id) + ' Changed 3 to 1', ending="\n")
            elif art.type == 4:
                art.type = 9
                art.save()
                self.stdout.write(str(art.id) + ' Changed 4 to 9', ending="\n")
            elif art.type == 5:
                art.type = 8
                art.save()
                self.stdout.write(str(art.id) + ' Changed 5 to 8', ending="\n")

