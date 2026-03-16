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
        fields = '__all__'


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



        return token