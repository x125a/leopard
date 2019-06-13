from rest_framework import serializers
from asset.models import Node


class NodeSerializer(serializers.ModelSerializer):
    '''
    节点序列化
    '''

    class Meta:
        model = Node
        fields = ('nid', 'name', 'ip', 'port', 'status')
