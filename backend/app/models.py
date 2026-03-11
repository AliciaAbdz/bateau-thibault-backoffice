from django.db import models

class Utilisateur(models.Model) : 
    created_at = models.DateField(auto_now_add = True)
    name = models.CharField(max_length=100, blank=False, null=False)
    first_name = models.CharField(max_length=100, blank=False, null=False)
    role = models.CharField(max_length=100, default='user', null=False)
    email = models.CharField(unique=True, max_length=100, blank=False, null=False)
    password = models.CharField(max_length=200, blank=False, default='', null=False)
    last_connection = models.DateField(auto_now_add = True)
    last_modification = models.DateField(auto_now_add = True)
    