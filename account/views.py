from django.shortcuts import render
from django.http import HttpResponse


def login(request):

    return render(request, 'account/login.html')
    # return HttpResponse('login')


def enroll(request):
    return HttpResponse('enroll')


def logout(request):
    return HttpResponse('logout')
