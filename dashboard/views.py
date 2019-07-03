from django.shortcuts import render
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

import pandas as pd
import json
import datetime
import pymongo
from account.views import login_required

# @login_required
def index(request):
    return render(request, 'index.html')


class DaysList(APIView):
    def __init__(self, **kwargs):
        super(DaysList, self).__init__(**kwargs)
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client['every_day_num']
        self.demo = {
            'data_company': '企业信息',
            'data_company_project':'企业项目',
            'data_company_project_tender' :'项目招投标',
            'data_company_project_censor' : '项目施工图审查',
            'data_company_project_censor_engineer' : '施工图审查从业人员',
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
            start, end = now-datetime.timedelta(now.weekday()), now
        elif period == 'year':
            start, end = now.replace(day=1, month=1), now

        res = self.db['updata_adddata_num'].find({
            "data_time":{"$gte": str(start), "$lte": str(end)}
        }).sort("data_time", 1)
        self.client.close()

        data = []
        for row in res:
            del row['_id']
            tmp = {}
            date = row.pop('data_time')
            df = pd.DataFrame(list(row.values()))
            tmp['date'] = date.lstrip(self.year).lstrip('-')
            tmp['value'] = (df.iloc[:,0].sum(), df.iloc[:,1].sum())
            data.append(tmp)

        return Response(data)

    def post(self, request):
        yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
        date = request.POST.get('date', str(yesterday))
        if not date.startswith(self.year):
            date = '-'.join([self.year, date])

        res = self.db['updata_adddata_num'].find({'data_time':date})
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