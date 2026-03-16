from rest_framework import viewsets, generics
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    Utilisateur, Category, Product, Manufacturer,
    ManufacturerArticle, Retailer, RetailerArticle, Purchase, Sale   
)
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UtilisateurSerializer, CategorySerializer, ProductSerializer,
    ManufacturerSerializer, ManufacturerArticleSerializer,
    RetailerSerializer, RetailerArticleSerializer,
    PurchaseSerializer, SaleSerializer,CustomTokenObtainPairSerializer
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class ManufacturerArticleViewSet(viewsets.ModelViewSet):
    queryset = ManufacturerArticle.objects.all()
    serializer_class = ManufacturerArticleSerializer


class RetailerViewSet(viewsets.ModelViewSet):
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer


class RetailerArticleViewSet(viewsets.ModelViewSet):
    queryset = RetailerArticle.objects.all()
    serializer_class = RetailerArticleSerializer


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer



class RegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = Utilisateur.objects.create_user(**serializer.validated_data)
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UtilisateurSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Utilisateur créé avec succès"
        }, status=status.HTTP_201_CREATED)
        
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer