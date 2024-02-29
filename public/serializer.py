from rest_framework import serializers
from .models import Public, PublicArticle, PublicMenu, PublicFile

class PublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Public
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'path', 'title', 'note', 'header_image', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class PublicArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicArticle
        fields = ('id', 'posted_by', 'posted_at', 'article', 'file')
        read_only_fields = ('id', 'posted_by', 'posted_at')

class PublicMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicMenu
        fields = ('id', 'updated_by', 'updated_at', 'title', 'url', 'order')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class PublicFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicFile
        fields = ('id', 'updated_by', 'updated_at', 'url', 'key', 'filename')
        read_only_fields = ('id', 'updated_by', 'updated_at')
