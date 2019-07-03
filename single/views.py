from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import auth
from django.conf import settings

from scrapyd_api import ScrapydAPI

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

import pandas as pd
import json
import datetime
import pymongo
import requests

from account.utils import get_valid_img
from single.models import Node
from single.serializers import NodeSerializer


def login_required(fun):
    '''用户登陆验证'''

    def wrapper(request, *args, **kwargs):
        try:
            session = request.session
            if 'checkcode' in session and 'user' in session:
                return fun(request, *args, **kwargs)
            else:
                return redirect('/login/')
        except Exception as e:
            return JsonResponse(str(e))

    return wrapper


@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def node(request):
    return render(request, 'node.html')


@login_required
def project(request):
    return render(request, 'project.html')


def scrapyd_obj(url):
    return ScrapydAPI(url)


def uri(ip, port):
    return 'http://{ip}:{port}'.format(ip=ip, port=port)


def check(request):
    img = get_valid_img(request)
    return HttpResponse(img)


@api_view(['GET', 'POST'])
def login(request):
    res = {'status': 1, 'msg': '登陆成功', 'data': None}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        checkcode = request.POST['checkcode'].upper()

        # 验证码
        if checkcode and checkcode == request.session['checkcode']:
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                request.session['user'] = True
                res['data'] = '/'
            else:
                res['status'], res['msg'] = 0, '用户名或密码错误'
        else:
            res['status'], res['msg'] = 0, '验证码错误'
        return Response(res)

    return render(request, 'login.html')


@login_required
def logout(request):
    try:
        del request.session['checkcode']
        del request.session['user']
    except Exception as e:
        print(e)
    return redirect('/login/')


class DaysList(APIView):
    '''数据统计'''

    def __init__(self, **kwargs):
        super(DaysList, self).__init__(**kwargs)
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client['every_day_num']
        self.demo = {
            'data_company': '企业信息',
            'data_company_project': '企业项目',
            'data_company_project_tender': '项目招投标',
            'data_company_project_censor': '项目施工图审查',
            'data_company_project_censor_engineer': '施工图审查从业人员',
            'data_company_project_contract': '项目合同备案',
            'data_company_project_builder_licence': '项目施工许可',
            'data_company_project_finish': '项目竣工验收备案',
            'data_cert': '资质',
            'data_engineer': '注册人员',
            'data_company_record': '外省备案',
            'data_company_record_engineer': '外省备案人员',
        }
        self.year = str(datetime.datetime.now().year)

    def get(self, request):
        now = datetime.datetime.now().date()
        period = request.query_params.dict().get('period')
        if period == 'month':
            start, end = now.replace(day=1), now
        elif period == 'week':
            start, end = now - datetime.timedelta(now.weekday()), now
        elif period == 'year':
            start, end = now.replace(day=1, month=1), now

        res = self.db['updata_adddata_num'].find({
            "data_time": {"$gte": str(start), "$lte": str(end)}
        }).sort("data_time", 1)
        self.client.close()

        data = []
        for row in res:
            del row['_id']
            tmp = {}
            date = row.pop('data_time')
            df = pd.DataFrame(list(row.values()))
            tmp['date'] = date.lstrip(self.year).lstrip('-')
            tmp['value'] = (df.iloc[:, 0].sum(), df.iloc[:, 1].sum())
            data.append(tmp)

        return Response(data)

    def post(self, request):
        yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
        date = request.POST.get('date', str(yesterday))
        if not date.startswith(self.year):
            date = '-'.join([self.year, date])

        res = self.db['updata_adddata_num'].find({'data_time': date})
        tmp = {}
        for row in res:
            del row['_id']

            tmp['date'] = row.pop('data_time')
            item = []
            add = []
            update = []

            for k, v in row.items():
                item.append(self.demo[k])
                add.append(v[1])
                update.append(v[0])
            tmp['add'] = add
            tmp['update'] = update
            tmp['item'] = item
        self.client.close()
        return Response(tmp)


class PorjectList(APIView):
    '''工程列表'''

    def get(self, request):
        nodes = Node.objects.all()
        for node in nodes:
            try:
                scrapyd = scrapyd_obj(uri(node.ip, node.port))
                for project in scrapyd.list_projects():
                    spiders = scrapyd.list_spiders(project)
                    print(spiders)
            except:
                pass
        return Response()


class NodeList(APIView):
    '''节点列表'''

    def get_status(self, pk):
        try:
            node = Node.objects.get(nid=pk)
            resp = requests.get(uri(node.ip, node.port), timeout=1)
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
    '''节点'''

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
        serializer = NodeSerializer(node, data=request.POST.dict())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, pk):
        node = self.get_row(pk)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
