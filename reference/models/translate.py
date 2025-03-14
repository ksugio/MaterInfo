from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote
from .text import Text
import requests

class Translate(Created, Updated, Remote):
    upper = models.ForeignKey(Text, verbose_name='Text', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)
    TranslateChoices = ((0, 'DeepL API Free'), (1, 'DeepL API'))
    translate = models.PositiveSmallIntegerField(verbose_name='Translate', choices=TranslateChoices, default=0)
    sourcel = models.CharField(verbose_name='Source Language', max_length=10, default='EN')
    targetl = models.CharField(verbose_name='Target Language', max_length=10, default='JA')
    text = models.TextField(verbose_name='Text', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:translate_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('reference:translate_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:translate_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:translate_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('reference:api_translate_update', kwargs={'pk': self.id})

    def deepl_api(self, api_key, text, free=True):
        if free:
            url = "https://api-free.deepl.com/v2/translate"
        else:
            url = "https://api.deepl.com/v2/translate"
        params = {
            'auth_key': api_key,
            'text': text,
            'source_lang': self.sourcel,
            'target_lang': self.targetl
        }
        request = requests.post(url, data=params)
        if request.status_code == 200:
            result = request.json()
            return result['translations'][0]['text']
        else:
            return text

    def set_text(self, api_key):
        if self.translate == 0:
            self.text = self.deepl_api(api_key, self.upper.text, True)
        elif self.translate == 1:
            self.text = self.deepl_api(api_key, self.upper.text, False)
