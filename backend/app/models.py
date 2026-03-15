from django.db import models

class Utilisateur(models.Model) : 
    created_at = models.DateField(auto_now_add = True)
    name = models.CharField(max_length=100, blank=False, null=False)
    first_name = models.CharField(max_length=100, blank=False, null=False)
    role = models.CharField(max_length=100, default='ROLE_USER', null=False)
    email = models.CharField(unique=True, max_length=100, blank=False, null=False)
    password = models.CharField(max_length=200, blank=False, default='', null=False)
    last_connection = models.DateField(auto_now_add = True)
    last_modification = models.DateField(auto_now_add = True)

class Category (models.Model) :
    name = models.CharField(max_length=100, blank=False, null=False)

class Product (models.Model) :
    name = models.CharField(max_length=100, blank=False, null=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    global_quantity = models.IntegerField(default=0)
class Manufacturer (models.Model) :
    name = models.CharField(max_length=200, blank=False, null=False)
    address = models.CharField(max_length=200, blank=False, null=False)
    
class ManufacturerArticle (models.Model) :
    unit = models.CharField(max_length=5, blank=False, null=False)
    availability = models.BooleanField(default=True)
    sales = models.BooleanField(default=False)
    comments = models.TextField()
    prod_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    manufacturer_id = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    
class Retailer (models.Model) :
    name = models.CharField(max_length=200, blank=False, null=False)
    address = models.CharField(max_length=200, blank=False, null=False)

    
class RetailerArticle (models.Model) :
    discount = models.IntegerField(default=0)
    image= models.TextField()
    unit_price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    is_archived = models.BooleanField(default=False)
    tig_id= models.ForeignKey(ManufacturerArticle, on_delete=models.CASCADE)
    id_retail= models.ForeignKey(Retailer, on_delete=models.CASCADE)


class Purchase (models.Model) :
    date= models.DateField(auto_now_add = True)
    total= models.IntegerField(default=0)
    quantity= models.IntegerField(default=0)
    id_retailer_article= models.ForeignKey(RetailerArticle, on_delete=models.CASCADE)


class Sale (models.Model) :
    date= models.DateField(auto_now_add = True)
    total= models.IntegerField(default=0)
    quantity= models.IntegerField(default=0)
    id_retailer_article= models.ForeignKey(RetailerArticle, on_delete=models.CASCADE)

