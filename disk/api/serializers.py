from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from .models import Item, FILE, FOLDER, calc_size 

class RepresentSerializer(serializers.ModelSerializer):
    """Для отображения элемента"""
    id = serializers.UUIDField()
    type = serializers.CharField()
    size = serializers.IntegerField()
    url = serializers.CharField()
    date = serializers.DateTimeField()
    parentId = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'type', 'size', 'parentId', 'url', 'date')
        model = Item

    def get_parentId(self, item):
        if item.parent:
            return item.parent.id
        else:
            return item.parent

class CreateSerializer(serializers.ModelSerializer):
    """Для создания элемента"""
    id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=[FILE, FOLDER], required = True)
    size = serializers.IntegerField(required = False)
    url = serializers.CharField(required = False)
    date = serializers.DateTimeField()
    parentId = serializers.UUIDField(allow_null = True, required = True)

    class Meta:
        fields = ('id', 'type', 'size', 'parentId', 'url', 'date')
        model = Item

    def validate(self, data):
        size = data.get('size')
        type = data.get('type')
        url = data.get('url')
        err_m = {}
        if type == FOLDER:
            if url is not None:
                err_m['url'] = 'Should be null for folders'
            if size is not None:
                err_m['size'] = 'Should be null for folders'
        else:
            if size <= 0:
                err_m['size'] = 'Should be > 0 for files'
        if err_m:
            raise ValidationError(err_m)
        return data
            
class ImportsSerializer(serializers.Serializer):
    """Для импорта элементов"""
    items = CreateSerializer(many = True)
    updateDate = serializers.DateTimeField()

    class Meta:
        fields = ('items', 'updateDate')

    @atomic
    def create(self, data):
        items = data.get('items')
        updateDate = data.get('updateDate')
        id_list = []
        for item_data in items:
            item_id = item_data.pop('id')
            if item_id in id_list:
                raise ValidationError(
                    'One request cannot have two elements with the same id'
                )
            element = Item.objects.filter(id = item_id).first()
            prev_parent = None
            if element:
                prev_parent = element.parent
            parent_id = item_data.pop('parentId')
            if parent_id:
                parent = Item.objects.filter(id=parent_id)
                if not parent.exists():
                    raise ValidationError(
                        {'parentId': 'Folder with such id doesn\'t exist'}
                    )
                parent = parent[0]
                if parent.type != FOLDER:
                    raise ValidationError(
                        {'parentId': 'Only folder can be parent'}
                    )
            else:
                parent = None
            Item.objects.update_or_create(
                defaults={
                    'type': item_data.get('type'),
                    'url': item_data.get('url'),
                    'size': item_data.get('size'),
                    'date': item_data.get('date'),
                    'parent': parent,
                },
                id=item_id,
            )
            id_list.append(item_id)
            if prev_parent:
                calc_size(prev_parent)
        queryset = Item.objects.filter(id__in=id_list)
        serializer = RepresentSerializer(queryset, many=True)
        return {'items': serializer.data, 'updateDate': updateDate}

class NodesSerializerClass(serializers.ModelSerializer):
    id = serializers.UUIDField()
    type = serializers.CharField()
    size = serializers.IntegerField()
    url = serializers.CharField()
    date = serializers.DateTimeField()
    parentId = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    def get_parentId(self, obj):
        if obj.parent:
            return obj.parent.id
        else:
            return obj.parent

    def get_children(self, obj):
        if obj.type == FILE:
            return None
        else:
            children = Item.objects.filter(parent = obj.id)
            if children.exists():
                serializer = NodesSerializerClass(instance = children, many = True)
                return serializer.data
            return []

    class Meta:
        fields = ('type', 'id', 'size', 'url', 'parentId', 'date', 'children')
        model = Item