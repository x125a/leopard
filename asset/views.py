import requests
from django.shortcuts import render
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

from asset.models import Node
from asset.serializers import NodeSerializer
from asset.utils import scrapyd_api


def index(request):
    return render(request, 'asset/index.html')


def detail(request):
    # if request.method == 'GET':
    #     node = Node.objects.get(nid=pk)

    return render(request, 'asset/detail.html')

class NodeList(APIView):
    def get_status(self, pk):
        try:
            node = Node.objects.get(nid=pk)
            resp = requests.get(scrapyd_api(node.ip, node.port), timeout=1)
        except:
            return 0

        return 1 if resp.ok else 0

    def get(self, request):
        nodes = Node.objects.all()

        for node in nodes:
            node.status = self.get_status(node.nid)

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
        # data = {}
        # for k, v in request.POST.dict().items():
        #     data[k.strip('node--model')] = v
        # print(data)
        print(request.POST.dict())
        serializer = NodeSerializer(node, data=request.POST.dict())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
