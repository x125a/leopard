from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import auth

from rest_framework.response import Response
from rest_framework.decorators import api_view
from account.utils import get_valid_img


def login_required(fun):
    '''用户登陆验证'''

    def wrapper(request, *args, **kwargs):
        try:
            session = request.session
            if 'checkcode' in session and 'user' in session:
                return fun(request, *args, **kwargs)
            else:
                return redirect('/account/login/')
        except Exception as e:
            return JsonResponse(str(e))

    return wrapper


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
                res['data'] = '/asset/'
            else:
                res['status'], res['msg'] = 0, '用户名或密码错误'
        else:
            res['status'], res['msg'] = 0, '验证码错误'
        return Response(res)

    return render(request, 'account/login.html')


def enroll(request):
    return HttpResponse('enroll')


def logout(request):
    try:
        del request.session['checkcode']
        del request.session['user']
    except Exception as e:
        print(e)
    return redirect('/account/login/')


def check(request):
    img = get_valid_img(request)
    return HttpResponse(img)
