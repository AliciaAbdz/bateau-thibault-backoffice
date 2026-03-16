from django.db import models
from django.contrib.auth.models import AbstractUser

class Retailer (models.Model) :
    name = models.CharField(max_length=200, blank=False, null=False)
    address = models.CharField(max_length=200, blank=False, null=False)


class Utilisateur(AbstractUser) :
    role = models.CharField(max_length=100, default='ROLE_USER', null=False)
    last_modification = models.DateField(auto_now=True)
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE, related_name='utilisateur', null=True, blank=True)

class Category (models.Model) :
    name = models.CharField(max_length=100, blank=False, null=False)

class Product (models.Model) :
    name = models.CharField(max_length=100, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    global_quantity = models.IntegerField(default=0)
class Manufacturer (models.Model) :
    name = models.CharField(max_length=200, blank=False, null=False)
    address = models.CharField(max_length=200, blank=False, null=False)
    
class ManufacturerArticle (models.Model) :
    unit = models.CharField(max_length=5, blank=False, null=False)
    availability = models.BooleanField(default=True)
    sales = models.IntegerField(default=0)
    comments = models.TextField()
    prod = models.ForeignKey(Product, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    

class RetailerArticle (models.Model) :
    discount = models.IntegerField(default=0)
    image= models.TextField()
    unit_price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    is_archived = models.BooleanField(default=False)
    tig= models.ForeignKey(ManufacturerArticle, on_delete=models.CASCADE)
    retail= models.ForeignKey(Retailer, on_delete=models.CASCADE)


class Purchase (models.Model) :
    date= models.DateField(auto_now_add = True)
    total= models.IntegerField(default=0)
    quantity= models.IntegerField(default=0)
    retailer_article= models.ForeignKey(RetailerArticle, on_delete=models.CASCADE)


class Sale (models.Model) :
    date= models.DateField(auto_now_add = True)
    total= models.IntegerField(default=0)
    quantity= models.IntegerField(default=0)
    retailer_article= models.ForeignKey(RetailerArticle, on_delete=models.CASCADE)

