from rest_framework import serializers
from .models import Document, File

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'created_by', 'created_at', 'file', 'comment', 'edition', 'filename')
        read_only_fields = ('id', 'created_by', 'created_at')
