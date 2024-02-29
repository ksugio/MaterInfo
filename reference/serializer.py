from rest_framework import serializers
from .models import Reference, Article

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'author', 'journal', 'volume', 'year', 'page',
                  'url', 'file', 'type', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')
