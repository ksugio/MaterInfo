from rest_framework import serializers
from .models.plot import Plot
from .models.area import Area
from .models.item import Item

class PlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plot
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'ncol', 'sizex', 'sizey')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'updated_by', 'updated_at', 'xlabel', 'ylabel',
                  'xmin', 'xmax', 'ymin', 'ymax', 'legend', 'order')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'updated_by', 'updated_at', 'url', 'columnx', 'columny', 'type',
                  'color', 'edgecolor', 'linewidth', 'linestyle', 'marker', 'markersize',
                  'bins', 'columnc', 'colormap', 'label', 'order')
        read_only_fields = ('id', 'updated_by', 'updated_at')
