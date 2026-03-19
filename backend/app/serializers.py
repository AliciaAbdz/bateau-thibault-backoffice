from rest_framework import serializers
from .models import (
    Utilisateur, Category, Product, Manufacturer,
    ManufacturerArticle, Retailer, RetailerArticle, Purchase, Sale
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        exclude = ['password']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 'retailer']

    def create(self, validated_data):
        return Utilisateur.objects.create_user(**validated_data)


class RetailerSerializer(serializers.ModelSerializer):
    # Récupère les utilisateurs liés via related_name='utilisateur'
    utilisateur = UtilisateurSerializer(many=True, read_only=True)

    class Meta:
        model = Retailer
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class ManufacturerArticleSerializer(serializers.ModelSerializer):
    prod = ProductSerializer(read_only=True)
    manufacturer = ManufacturerSerializer(read_only=True)

    class Meta:
        model = ManufacturerArticle
        fields = '__all__'


class RetailerArticleSerializer(serializers.ModelSerializer):
    tig = ManufacturerArticleSerializer(read_only=True)
    retail = RetailerSerializer(read_only=True)

    class Meta:
        model = RetailerArticle
        fields = '__all__'


class RetailerArticleFlatSerializer(serializers.ModelSerializer):
    """Serializer aplati pour le frontend - correspond à l'interface RetailArticle"""
    name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    price = serializers.IntegerField(source='unit_price')
    discount_percent = serializers.IntegerField(source='discount')
    stock = serializers.IntegerField(source='quantity')
    sales = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    class Meta:
        model = RetailerArticle
        fields = ['id', 'name', 'category', 'price', 'discount_percent',
                  'stock', 'sales', 'comment']

    def get_name(self, obj):
        return obj.tig.prod.name

    def get_category(self, obj):
        return obj.tig.prod.category.name

    def get_sales(self, obj):
        return obj.tig.sales

    def get_comment(self, obj):
        return obj.tig.comments


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Appeler la méthode parent pour avoir le token de base
        token = super().get_token(user)

        # Ajouter des claims personnalisés
        token['retailer'] =  user.retailer_id 
        token['role'] = user.role
        token['last_connexion'] = str(user.last_login) if user.last_login else None



        return token