from django.db import models

class Utilisateur(models.Model) : 
    created_at = models.DateField(auto_now_add = True)
    name = models.CharField(max_length=100, blank=False, default='username')
    first_name = models.CharField(max_length=100, blank=False, default='userfirstname')