from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UtilisateurViewSet, CategoryViewSet, ProductViewSet,
    ManufacturerViewSet, ManufacturerArticleViewSet,
    RetailerViewSet, RetailerArticleViewSet,
    PurchaseViewSet, SaleViewSet,
    RegisterView,CustomTokenObtainPairView  # ← Ajoute tes nouvelles views
)

router = DefaultRouter()
router.register('utilisateurs', UtilisateurViewSet)
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('manufacturers', ManufacturerViewSet)
router.register('manufacturer-articles', ManufacturerArticleViewSet)
router.register('retailers', RetailerViewSet)
router.register('retailer-articles', RetailerArticleViewSet)
router.register('purchases', PurchaseViewSet)
router.register('sales', SaleViewSet)

# Combiner les URLs du router avec tes endpoints custom
urlpatterns = [
    # Auth endpoints (JWT)
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('auth/me/', CurrentUserView.as_view(), name='current_user'),
    
    # Routes du router (tous tes ViewSets)
    path('', include(router.urls)),
]