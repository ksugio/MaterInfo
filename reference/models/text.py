from django.db import models
from django.urls import reverse
from project.models import Created, Updated, Remote
from .article import Article
from io import BytesIO
import pymupdf
import pymupdf4llm
import json

class Text(Created, Updated, Remote):
    upper = models.ForeignKey(Article, verbose_name='Article', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=100)
    note = models.TextField(verbose_name='Note', blank=True)
    start = models.PositiveSmallIntegerField(verbose_name='Start Page', blank=True, null=True)
    end = models.PositiveSmallIntegerField(verbose_name='End Page', blank=True, null=True)
    text = models.TextField(verbose_name='Text', blank=True)
    nimages = models.PositiveSmallIntegerField(verbose_name='Number of images', default=0)
    tables = models.TextField(verbose_name='Tables', blank=True)

    def __str__(self):
        return self.title

    def get_list_url(self):
        return reverse('reference:text_list', kwargs={'pk': self.upper.id})

    def get_detail_url(self):
        return reverse('reference:text_detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('reference:text_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('reference:text_delete', kwargs={'pk': self.id})

    def get_apiupdate_url(self):
        return reverse('reference:api_text_update', kwargs={'pk': self.id})

    def open_pdf(self):
        if self.upper.file:
            with self.upper.file.open('rb') as f:
                buf = BytesIO(f.read())
                doc = pymupdf.open(stream=buf.getvalue(), filetype='pdf')
                buf.close()
            return doc
        else:
            return None

    def check_page(self, page):
        if self.start and page < self.start:
            return False
        elif self.end and page > self.end:
            return False
        else:
            return True

    def get_images(self, doc):
        imgs = []
        for i in range(doc.page_count):
            if self.check_page(i + 1):
                imgs.extend(doc.get_page_images(i))
        return imgs

    def get_tables(self, doc):
        tabs = []
        for page in doc:
            if self.check_page(page.number + 1):
                for tb in page.find_tables():
                    tabs.append(tb.extract())
        return tabs

    def set_text(self):
        doc = self.open_pdf()
        if doc is not None:
            if self.start:
                start = self.start - 1
            else:
                start = 0
            if self.end:
                end = self.end - 1
            else:
                end = doc.page_count
            pages = [i for i in range(start, end)]
            self.text = pymupdf4llm.to_markdown(doc, pages=pages)
            imgs = self.get_images(doc)
            self.nimages = len(imgs)
            tabs = self.get_tables(doc)
            self.tables = json.dumps(tabs)

    def extract_pixmap(self, iid):
        doc = self.open_pdf()
        imgs = self.get_images(doc)
        if iid >= 0 and iid < len(imgs):
            xref = imgs[iid][0]
            pix = pymupdf.Pixmap(doc.extract_image(xref)['image'])
            smask = imgs[iid][1]
            if smask != 0:
                mask = pymupdf.Pixmap(doc.extract_image(smask)['image'])
                pix = pymupdf.Pixmap(pix, mask)
            if pix.colorspace.name == 'DeviceCMYK':
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            return pix
        else:
            return None
