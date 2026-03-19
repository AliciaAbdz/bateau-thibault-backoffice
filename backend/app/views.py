from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .models import (
    Utilisateur, Category, Product, Manufacturer,
    ManufacturerArticle, Retailer, RetailerArticle, Purchase, Sale
)
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UtilisateurSerializer, RegisterSerializer, CategorySerializer, ProductSerializer,
    ManufacturerSerializer, ManufacturerArticleSerializer,
    RetailerSerializer, RetailerArticleSerializer, RetailerArticleFlatSerializer,
    PurchaseSerializer, SaleSerializer, CustomTokenObtainPairSerializer
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
    queryset = RetailerArticle.objects.select_related(
        'tig__prod__category', 'tig__manufacturer', 'retail'
    ).filter(is_archived=False)
    serializer_class = RetailerArticleFlatSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrer par retailer si paramètre ?retail=X
        retail_id = self.request.query_params.get('retail')
        if retail_id:
            queryset = queryset.filter(retail_id=retail_id)
        return queryset

    def get_serializer_class(self):
        # Utiliser le serializer nested pour les écritures (POST/PUT/PATCH)
        if self.action in ['create', 'update', 'partial_update']:
            return RetailerArticleSerializer
        # Serializer aplati pour la lecture (GET)
        return RetailerArticleFlatSerializer

    @action(detail=False, methods=['post'], url_path='submit-changes', permission_classes=[AllowAny])
    def submit_changes(self, request):
        """
        Reçoit une liste de modifications :
        [
          { "id": 12, "quantity_change": 106, "is_expired": false, "purchase_price": 15 },
          { "id": 7,  "quantity_change": -27, "is_expired": false },
          { "id": 3,  "quantity_change": -20, "is_expired": true }
        ]
        """
        changes = request.data
        if not isinstance(changes, list):
            return Response(
                {"error": "Une liste de modifications est attendue"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_purchases = []
        created_sales = []

        try:
            # transaction.atomic = tout passe ou tout échoue
            with transaction.atomic():
                for item in changes:
                    article_id = item.get('id')
                    quantity_change = item.get('quantity_change', 0)
                    is_expired = item.get('is_expired', False)
                    purchase_price = item.get('purchase_price', 0)

                    if quantity_change == 0:
                        continue

                    # select_for_update verrouille la ligne en BDD
                    # pour éviter les conflits si 2 users modifient en même temps
                    article = RetailerArticle.objects.select_for_update().get(id=article_id)

                    if quantity_change > 0:
                        # ACHAT : on ajoute au stock + on crée un Purchase
                        article.quantity += quantity_change
                        article.save()
                        purchase = Purchase.objects.create(
                            retailer_article=article,
                            quantity=quantity_change,
                            total=quantity_change * purchase_price
                        )
                        created_purchases.append({
                            "id": purchase.id,
                            "article_id": article_id,
                            "quantity": quantity_change,
                            "total": purchase.total
                        })

                    elif not is_expired:
                        # VENTE : on retire du stock + on crée un Sale au prix de vente
                        article.quantity += quantity_change  # négatif donc soustrait
                        article.save()
                        sale = Sale.objects.create(
                            retailer_article=article,
                            quantity=abs(quantity_change),
                            total=abs(quantity_change) * article.unit_price
                        )
                        created_sales.append({
                            "id": sale.id,
                            "article_id": article_id,
                            "quantity": abs(quantity_change),
                            "total": sale.total,
                            "type": "vente"
                        })

                    else:
                        # PERTE : on retire du stock + on crée un Sale à 0€
                        article.quantity += quantity_change  # négatif
                        article.save()
                        sale = Sale.objects.create(
                            retailer_article=article,
                            quantity=abs(quantity_change),
                            total=0
                        )
                        created_sales.append({
                            "id": sale.id,
                            "article_id": article_id,
                            "quantity": abs(quantity_change),
                            "total": 0,
                            "type": "perte"
                        })

        except RetailerArticle.DoesNotExist:
            return Response(
                {"error": f"Article {article_id} introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message": "Modifications enregistrées",
            "purchases": created_purchases,
            "sales": created_sales
        }, status=status.HTTP_200_OK)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer



class RegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
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