from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from config.settings import RANDOM_STRING_LENGTH
from accounts.models import CustomUser
from project.models import Created, Updated
from article.models import Article
import os
import requests

def HeaderImageUploadTo(instance, filename):
    split = os.path.splitext(os.path.basename(filename))
    newname = 'HeaderImage_%s%s' % (get_random_string(length=RANDOM_STRING_LENGTH), split[1])
    return 'public/%s' % newname

def PublicUploadTo(instance, filename):
    split = os.path.splitext(os.path.basename(filename))
    newname = '%s_%s%s' % (split[0], get_random_string(length=RANDOM_STRING_LENGTH), split[1])
    return 'public/%s' % newname

class Public(Created, Updated):
    title = models.CharField(verbose_name='Title', max_length=100)
    path = models.CharField(verbose_name='Path', max_length=32)
    note = models.TextField(verbose_name='Note', blank=True)
    header_color = models.CharField(verbose_name='Header Color', max_length=32, default='#F5F5F5')
    header_image = models.ImageField(verbose_name='Header Image', blank=True, upload_to=HeaderImageUploadTo)
    style_css = models.TextField(verbose_name='Style CSS', blank=True)
    file = models.FileField(verbose_name='HTML File', upload_to=PublicUploadTo, blank=True, null=True)

    def get_list_url(self):
        return reverse('public:list')

    def get_detail_url(self):
        return reverse('public:detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('public:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('public:delete', kwargs={'pk': self.id})

    def get_header_image_url(self):
        return reverse('public:header_image', kwargs={'pk': self.id})

def GetPublicFile(url, request):
    response = requests.get(request._current_scheme_host + url,
                            headers=request.headers)
    if response.status_code == 200 and 'image' in response.headers['Content-Type']:
        ctype = response.headers['Content-Type']
        if ctype == 'image/jpeg':
            fname = 'PublicFile.jpg'
        elif ctype == 'image/png':
            fname = 'PublicFile.png'
        elif ctype == 'image/bmp':
            fname = 'PublicFile.bmp'
        elif ctype == 'image/tiff':
            fname = 'PublicFile.tif'
        else:
            fname = ''
        if fname:
            return InMemoryUploadedFile(ContentFile(response.content), None, fname,
                                        None, len(response.content), None)
        else:
            return None

class PublicArticle(models.Model):
    upper = models.ForeignKey(Public, verbose_name='Public', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)
    posted_by = models.ForeignKey(CustomUser, verbose_name='Posted by', on_delete=models.PROTECT)
    posted_at = models.DateTimeField(verbose_name='Posted at', default=timezone.now)
    file = models.FileField(verbose_name='HTML File', upload_to=PublicUploadTo, blank=True, null=True)

    def title(self):
        return self.article.title

    def get_list_url(self):
        return reverse('public:article_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('public:article_list', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('public:article_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('public:article_delete', kwargs={'pk': self.id})

    def check_url(self, url, changes):
        for change in changes:
            if url == change['url']:
                return False
        return True

    def modify_text(self, request, changes):
        lines = self.article.text.splitlines()
        for line in lines:
            st = line.find('](')
            ed = line.rfind(')')
            if st >= 0 and ed >= 0:
                url = line[st+2:ed]
                if not url.startswith('http') and self.check_url(url, changes):
                    items = PublicFile.objects.filter(upper=self.upper).filter(url=url)
                    if items:
                        params = {
                            'url': items[0].url,
                            'key': items[0].key,
                            'create': False
                        }
                        changes.append(params)
                    else:
                        file = GetPublicFile(url, request)
                        if file:
                            params = {
                                'url': url,
                                'key': get_random_string(length=RANDOM_STRING_LENGTH),
                                'file': file,
                                'create': True
                            }
                            changes.append(params)
        text = self.article.text
        for change in changes:
            text = text.replace(change['url'], "/public/file/{0}".format(change['key']))
        return text, changes

class PublicMenu(Updated):
    upper = models.ForeignKey(Public, verbose_name='Public', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    url = models.URLField(verbose_name="URL", max_length=200)
    order = models.SmallIntegerField(verbose_name='Order')

    def get_list_url(self):
        return reverse('public:menu_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('public:menu_list', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('public:menu_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('public:menu_delete', kwargs={'pk': self.id})

def RandomString():
    return get_random_string(length=RANDOM_STRING_LENGTH)

class PublicFile(Updated):
    upper = models.ForeignKey(Public, verbose_name='Public', on_delete=models.CASCADE)
    url = models.CharField(verbose_name='URL', max_length=100)
    key = models.CharField(verbose_name='Key', max_length=100)
    file = models.ImageField(verbose_name='Image', upload_to=PublicUploadTo, blank=True, null=True)
    header = models.BooleanField(verbose_name='Header', default=False)

    def title(self):
        return self.url

    def get_list_url(self):
        return reverse('public:file_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('public:file_list', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        return reverse('public:file_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('public:file_delete', kwargs={'pk': self.id})

    def set_file(self, request):
        file = GetPublicFile(self.url, request)
        if file:
            self.file = file
