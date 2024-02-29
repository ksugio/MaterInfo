from django.test import TestCase
from accounts.models import CustomUser
from .models import Project

class ProjectTestCase(TestCase):
    def setUp(self):
        user = CustomUser.objects.create(username='jiro')
        Project.objects.create(created_by=user, updated_by=user)

    def testProject(self):
        projects = Project.objects.all()
