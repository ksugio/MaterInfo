from rest_framework import serializers
from .models.reference import Reference
from .models.article import Article
from .models.image import Image
from .models.digitizer import Digitizer
from .models.text import Text
from .models.translate import Translate
from .models.clip import Clip

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'order', 'template', 'startid', 'data')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'type', 'key', 'title', 'author', 'journal', 'volume', 'number', 'month', 'year',
                  'pages', 'cited', 'impact', 'booktitle', 'publisher', 'address', 'doi', 'url',
                  'file', 'abstract', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'note', 'page', 'scale', 'rotate', 'startx', 'starty',
                  'endx', 'endy', 'zoom')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class DigitizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Digitizer
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'note', 'data', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'note', 'text', 'nimages')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class TranslateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translate
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'note', 'translate', 'sourcel', 'targetl', 'text')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'note', 'start', 'end', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')
