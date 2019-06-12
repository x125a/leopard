from django.shortcuts import render
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

from asset.models import Node
from asset.serializers import NodeSerializer


def index(request):
    return render(request, 'asset/index.html')


class NodeList(APIView):
    def get(self, request):
        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)

        return Response(serializer.data)


class NodeDetail(APIView):

    def get_row(self, pk):
        try:
            return Node.objects.get(nid=pk)
        except Node.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        node = self.get_row(pk)
        serializer = NodeSerializer(node)

        return Response(serializer.data)

    def post(self, request, pk):
        node = self.get_row(pk)
        data = {
            "nid": "400d75a5-21a5-451d-9aa2-ec17db3f78f4",
            "name": "本机",
            "ip": "127.0.0.200",
            "port": 6800
        }
        serializer = NodeSerializer(node, data=data)
        # serializer = NodeSerializer(node, data=request.POST.dict())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
