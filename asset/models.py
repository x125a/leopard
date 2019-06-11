from django.db import models

# Create your models here.

class Node(models.Model):
    '''节点'''
    name = models.CharField(max_length=255, default=None)
    ip = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(default=6800, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

