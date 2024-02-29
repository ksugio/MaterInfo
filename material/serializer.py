from rest_framework import serializers
from .models import Material, Element

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'fraction', 'file', 'percent_in', 'template')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = ('id', 'updated_by', 'updated_at', 'element', 'fraction')
        read_only_fields = ('id', 'updated_by', 'updated_at')
