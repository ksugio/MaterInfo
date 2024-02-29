from rest_framework import serializers
from .models import Comment, Response

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'created_by', 'created_at', 'title', 'comment', 'file')
        read_only_fields = ('id', 'created_by', 'created_at')

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('id', 'created_by', 'created_at', 'response', 'file')
        read_only_fields = ('id', 'created_by', 'created_at')
