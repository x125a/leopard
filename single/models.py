from django.db import models
from django.contrib.auth.models import User
import uuid

class UserPorfile(models.Model):
    '''用户表'''
    user = models.OneToOneField(User, on_delete='models.CASCADE')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'User'
        
class Node(models.Model):
    '''节点'''
    nid = models.UUIDField(default=uuid.uuid4, primary_key=True, null=False)
    name = models.CharField(max_length=255, default=None)
    ip = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(default=6800, blank=True, null=True)
    status = models.IntegerField(default=1, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Node'

# class Project(models.Model):
#     '''工程'''
