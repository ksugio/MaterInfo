from rest_framework import serializers
from .models import Poll, Question, Answer

class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'updated_by', 'updated_at', 'question', 'order')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'upper', 'updated_by', 'updated_at', 'answer')
        read_only_fields = ('id', 'upper', 'updated_by', 'updated_at')
