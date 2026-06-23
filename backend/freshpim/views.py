from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.models import Utilisateur

from .models import (
    Family, Attribute, FamilyAttribute,
    PIMProduct, AttributeValue, Translation, Asset,
)
from .permissions import (
    PIMReferentialPermission, PIMProductPermission,
    _is_pim_admin, _is_manufacturer,
)
from .serializers import (
    FamilySerializer, AttributeSerializer, FamilyAttributeSerializer,
    PIMProductListSerializer, PIMProductDetailSerializer,
    TranslationSerializer, AttributeValueSerializer, AssetSerializer,
)


# ---------- Référentiel (familles + attributs) ----------

class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.prefetch_related('familyattribute_set__attribute').all()
    serializer_class = FamilySerializer
    permission_classes = [PIMReferentialPermission]


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [PIMReferentialPermission]


class FamilyAttributeViewSet(viewsets.ModelViewSet):
    queryset = FamilyAttribute.objects.select_related('family', 'attribute').all()
    serializer_class = FamilyAttributeSerializer
    permission_classes = [PIMReferentialPermission]


# ---------- Produits PIM ----------

class PIMProductViewSet(viewsets.ModelViewSet):
    queryset = PIMProduct.objects.select_related('family', 'created_by').prefetch_related(
        'translations', 'attribute_values__attribute', 'assets',
    )
    permission_classes = [PIMProductPermission]

    def get_serializer_class(self):
        if self.action == 'list':
            return PIMProductListSerializer
        return PIMProductDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if _is_pim_admin(user):
            pass  # voit tout
        elif _is_manufacturer(user):
            qs = qs.filter(created_by=user)
        else:
            qs = qs.filter(status=PIMProduct.STATUS_PUBLISHED)

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        family_param = self.request.query_params.get('family')
        if family_param:
            qs = qs.filter(family_id=family_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status=PIMProduct.STATUS_DRAFT)

    # ----- workflow -----

    # Transitions autorisées : depuis → vers
    ALLOWED_TRANSITIONS = {
        PIMProduct.STATUS_DRAFT: {PIMProduct.STATUS_IN_REVIEW},
        PIMProduct.STATUS_IN_REVIEW: {PIMProduct.STATUS_PUBLISHED, PIMProduct.STATUS_DRAFT},
        PIMProduct.STATUS_PUBLISHED: {PIMProduct.STATUS_ARCHIVED},
        PIMProduct.STATUS_ARCHIVED: {PIMProduct.STATUS_DRAFT},
    }
    MIN_COMPLETENESS_TO_PUBLISH = 80

    @action(detail=True, methods=['post'], url_path='transition')
    def transition(self, request, pk=None):
        """
        Transition de statut. Body : { "to": "in_review" | "published" | "draft" | "archived" }.

        - draft → in_review : MANUFACTURER (propriétaire) ou PIM_ADMIN
        - in_review → published : PIM_ADMIN uniquement, exige completeness ≥ 80%
        - in_review → draft : PIM_ADMIN (rejet, renvoie au fournisseur)
        - published → archived : PIM_ADMIN
        - archived → draft : PIM_ADMIN (réouverture)
        """
        product = self.get_object()
        target = request.data.get('to')

        if target not in dict(PIMProduct.STATUS_CHOICES):
            return Response({"error": f"Statut cible invalide : {target}"}, status=status.HTTP_400_BAD_REQUEST)

        allowed = self.ALLOWED_TRANSITIONS.get(product.status, set())
        if target not in allowed:
            return Response(
                {"error": f"Transition interdite : {product.status} → {target}",
                 "allowed_from_current": list(allowed)},
                status=status.HTTP_409_CONFLICT,
            )

        user = request.user
        # Règles d'autorisation par transition
        if target == PIMProduct.STATUS_IN_REVIEW:
            if not (_is_pim_admin(user) or (_is_manufacturer(user) and product.created_by_id == user.id)):
                return Response({"error": "Seul le propriétaire ou le PIM_ADMIN peut soumettre."},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            if not _is_pim_admin(user):
                return Response({"error": "Seul le PIM_ADMIN peut effectuer cette transition."},
                                status=status.HTTP_403_FORBIDDEN)

        # Garde-fou de complétude pour publier
        if target == PIMProduct.STATUS_PUBLISHED:
            product.completeness = product.compute_completeness()
            if product.completeness < self.MIN_COMPLETENESS_TO_PUBLISH:
                return Response(
                    {"error": f"Complétude insuffisante : {product.completeness}% (min {self.MIN_COMPLETENESS_TO_PUBLISH}%)."},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            product.published_at = timezone.now()

        product.status = target
        product.save()  # déclenche le signal sync_to_freshpilot si target=published

        return Response(PIMProductDetailSerializer(product).data, status=status.HTTP_200_OK)


# ---------- Ressources liées (translations / attribute_values / assets) ----------

class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.select_related('product').all()
    serializer_class = TranslationSerializer
    permission_classes = [PIMProductPermission]


class AttributeValueViewSet(viewsets.ModelViewSet):
    queryset = AttributeValue.objects.select_related('product', 'attribute').all()
    serializer_class = AttributeValueSerializer
    permission_classes = [PIMProductPermission]

    def perform_create(self, serializer):
        instance = serializer.save()
        product = instance.product
        product.completeness = product.compute_completeness()
        product.save(update_fields=['completeness'])

    def perform_update(self, serializer):
        instance = serializer.save()
        product = instance.product
        product.completeness = product.compute_completeness()
        product.save(update_fields=['completeness'])


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('product').all()
    serializer_class = AssetSerializer
    permission_classes = [PIMProductPermission]


# ---------- Export omnicanal ----------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def omnichannel_export(request):
    """
    GET /api/pim/export?channel=<canal>&lang=<locale>

    Diffusion omnicanale : exporte toutes les fiches PIM publiées dans le format
    attendu par le canal de consommation. Le PIM est la source unique de vérité,
    chaque canal récupère uniquement ce dont il a besoin.

    Canaux supportés :
      - pos          : POS / back-office point de vente (ex: FreshPilot).
                       Format minimal : SKU + nom + catégorie + image principale.
                       C'est le canal "interne" du groupe.

    Canaux planifiés (non implémentés ici, voir docstrings ci-dessous) :
      - ecommerce    : sites e-commerce (decathlon.fr-like).
      - mobile       : applications mobiles (payload allégé).
      - marketplace  : marketplaces tierces (Amazon-like, format CSV-friendly).
    """
    channel = request.query_params.get('channel', 'pos')
    lang = request.query_params.get('lang', 'fr')

    if channel != 'pos':
        return Response(
            {"error": f"Canal '{channel}' non implémenté (stub uniquement).",
             "implemented_channels": ["pos"],
             "planned_channels": ["ecommerce", "mobile", "marketplace"]},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

    return Response(_export_pos(lang))


def _export_pos(lang):
    """
    Canal POS (FreshPilot et autres back-offices de point de vente).

    Payload minimal nécessaire à un POS :
      - sku : identifiant du référentiel (clé de jointure avec le POS)
      - name : libellé localisé du produit
      - family : nom de la famille (sert de catégorie côté POS)
      - main_image : URL de la 1ère image (asset à position=0)

    Le POS n'a pas besoin du marketing description, des assets HD, des traductions
    autres que celle qu'il consomme, ni des attributs techniques.
    """
    products = PIMProduct.objects.filter(status=PIMProduct.STATUS_PUBLISHED).select_related(
        'family',
    ).prefetch_related('translations', 'assets')

    payload = []
    for p in products:
        translation = next((t for t in p.translations.all() if t.locale == lang), None) \
            or next((t for t in p.translations.all() if t.locale == 'fr'), None) \
            or next(iter(p.translations.all()), None)
        if translation is None:
            continue
        main_image = next((a.url for a in p.assets.all() if a.type == Asset.TYPE_IMAGE), None)
        payload.append({
            "sku": p.sku,
            "name": translation.name,
            "family": p.family.name,
            "main_image": main_image,
        })
    return {
        "channel": "pos",
        "lang": lang,
        "count": len(payload),
        "items": payload,
    }


# ---------- Stubs des autres canaux (documentation pour le rapport) ----------

def _export_ecommerce(lang):  # noqa: F841
    """
    Canal e-commerce — non implémenté (stub).

    Payload attendu : tout le contenu enrichi.
      - sku, name (localisé), marketing_description (localisé)
      - family + breadcrumb catégorie
      - tous les attribute_values (typés, localisés si is_localizable)
      - assets ordonnés (images HD, vidéos, fiches PDF)
      - last_published_at pour le cache HTTP côté front
    """
    raise NotImplementedError


def _export_mobile(lang):  # noqa: F841
    """
    Canal mobile — non implémenté (stub).

    Payload allégé pour minimiser la consommation réseau.
      - sku, name, short_description (description tronquée à 150 caractères)
      - 1 image basse résolution (transformée à 400×400)
      - attribute_values uniquement pour les attributs marqués "essentiels"
    """
    raise NotImplementedError


def _export_marketplace(lang):  # noqa: F841
    """
    Canal marketplace — non implémenté (stub).

    Payload "plat" CSV-friendly, sans nested, compatible imports Amazon/Cdiscount.
      - sku, name, description, brand
      - colonnes attribute_<code> pour chaque attribut (une par colonne)
      - urls d'images séparées par |
    """
    raise NotImplementedError
