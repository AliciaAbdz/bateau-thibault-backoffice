from rest_framework.permissions import BasePermission, SAFE_METHODS

from app.models import Utilisateur


def _is_pim_admin(user):
    return bool(user and user.is_authenticated and user.role == Utilisateur.ROLE_PIM_ADMIN)


def _is_manufacturer(user):
    return bool(user and user.is_authenticated and user.role == Utilisateur.ROLE_MANUFACTURER)


class PIMReferentialPermission(BasePermission):
    """
    Référentiel (Family, Attribute, FamilyAttribute) :
    - lecture libre pour tout utilisateur authentifié
    - écriture réservée au ROLE_PIM_ADMIN (seuls eux configurent le gabarit)
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return _is_pim_admin(request.user)


class PIMProductPermission(BasePermission):
    """
    PIMProduct + ses ressources liées (translations, attribute_values, assets) :
    - PIM_ADMIN : tout
    - MANUFACTURER : lit/écrit uniquement ses propres fiches (created_by = lui)
    - autres rôles : lecture seule des fiches published

    Création (POST) réservée à MANUFACTURER et PIM_ADMIN : les autres rôles
    consomment le PIM, ils ne le remplissent pas.
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method == 'POST':
            return _is_pim_admin(user) or _is_manufacturer(user)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if _is_pim_admin(user):
            return True

        # Résoudre l'objet PIMProduct cible (obj peut être un Translation/Asset/AttributeValue)
        from .models import PIMProduct
        product = obj if isinstance(obj, PIMProduct) else getattr(obj, 'product', None)

        if _is_manufacturer(user):
            return product is not None and product.created_by_id == user.id

        # Autres rôles : lecture seule des fiches publiées
        if request.method in SAFE_METHODS:
            return product is not None and product.status == PIMProduct.STATUS_PUBLISHED
        return False
