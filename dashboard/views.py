from django.shortcuts import render
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

import pandas as pd
import json
import datetime
import pymongo

def index(request):
    return render(request, 'index.html')


class DaysList(APIView):
    def __init__(self, **kwargs):
        super(DaysList, self).__init__(**kwargs)
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client['every_day_num']

    def get(self, request):
        now = datetime.datetime.now().date()
        month = now.replace(day=1)

        res = self.db['updata_adddata_num'].find({
            "data_time":{"$gte": str(month), "$lte": str(now)}
        }).sort("data_time", 1)
        self.client.close()

        data = []
        for row in res:
            del row['_id']
            tmp = {}
            date = row.pop('data_time')
            df = pd.DataFrame(list(row.values()))
            tmp['date'] = date
            tmp['value'] = (df.iloc[:,0].sum(), df.iloc[:,1].sum())
        
            data.append(tmp)

        return Response(data)

    def post(self, request):
        yesterday = datetime.datetime.now().date() - datetime.timedelta(day=1)
        date = request.POST.get('date', str(yesterday))
        res = self.db['updata_adddata_num'].find({'data_time':date})
        
        data = []
        for row in res:
            del row['_id']

        return Response({})


# class DaysDetail()


