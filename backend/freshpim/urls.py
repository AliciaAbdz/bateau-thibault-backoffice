from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    FamilyViewSet, AttributeViewSet, FamilyAttributeViewSet,
    PIMProductViewSet, TranslationViewSet, AttributeValueViewSet, AssetViewSet,
    omnichannel_export,
)

router = SimpleRouter()
router.register('families', FamilyViewSet)
router.register('attributes', AttributeViewSet)
router.register('family-attributes', FamilyAttributeViewSet)
router.register('products', PIMProductViewSet)
router.register('translations', TranslationViewSet)
router.register('attribute-values', AttributeValueViewSet)
router.register('assets', AssetViewSet)

urlpatterns = [
    path('export/', omnichannel_export, name='pim-omnichannel-export'),
    path('', include(router.urls)),
]
