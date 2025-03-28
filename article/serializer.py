from rest_framework import serializers
from .models import Article, File, Diff

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'type', 'category', 'public', 'text', 'comment', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class PDFSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, write_only=True)

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'updated_by', 'updated_at', 'name', 'note',
                  'file', 'url', 'unique')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class DiffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diff
        fields = ('id', 'updated_by', 'updated_at', 'diff', 'comment')
        read_only_fields = ('id', 'updated_by')
