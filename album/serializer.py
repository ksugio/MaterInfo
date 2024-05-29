from rest_framework import serializers
from .models.album import Album
from .models.item import Item

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'ncol', 'margin', 'bgcolor', 'format',
                  'file', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'updated_by', 'updated_at', 'url', 'width', 'height',
                  'shiftx', 'shifty', 'order')
        read_only_fields = ('id', 'updated_by', 'updated_at')
