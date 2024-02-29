from django.test import TestCase
from accounts.models import CustomUser
from project.models import Project
from sample.models import Sample
from .models.image import Image
from .models.filter import Filter
from .models.process import Resize, Smoothing, Threshold, Molphology
from .models.size import Size

class ImageTestCase(TestCase):
    def setUp(self):
        user = CustomUser.objects.create(username='jiro')
        proj = Project.objects.create(title='Project_1', created_by=user, updated_by=user)
        samp = Sample.objects.create(title='Sample_1', created_by=user, updated_by=user, upper=proj)
        img = Image.objects.create(created_by=user, updated_by=user, upper=samp)
        fil = Filter.objects.create(created_by=user, updated_by=user, upper=img)
        Resize.objects.create(updated_by=user, upper=fil, type=0, order=10)
        Smoothing.objects.create(updated_by=user, upper=fil, type=1, order=20)
        Threshold.objects.create(updated_by=user, upper=fil, type=2, order=30)
        Molphology.objects.create(updated_by=user, upper=fil, type=3, order=40)
        for i in range(3):
            Size.objects.create(created_by=user, updated_by=user, upper=fil)

    def testImage(self):
        siz = Size.objects.all()
        for s in siz:
            print('Size', s.id, s.updated_by)