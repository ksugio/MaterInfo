from django.test import TestCase
from .models import CustomUser

class AccountsTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create(username='jiro')

    def testAccounts(self):
        user = CustomUser.objects.get(username='jiro')
        print('User', user.id)