from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import PIMProduct, Translation


@receiver(post_save, sender=PIMProduct)
def sync_pim_product_to_freshpilot(sender, instance, created, **kwargs):
    """
    Quand un PIMProduct est publié (status=published), on synchronise
    sa fiche dans le Product de FreshPilot lié (création si absent).

    On lit le nom depuis la Translation FR; sans elle on tombe sur n'importe
    quelle translation. Si aucune translation n'existe encore, on skip.
    """
    if instance.status != PIMProduct.STATUS_PUBLISHED:
        return

    if instance.published_at is None:
        PIMProduct.objects.filter(pk=instance.pk).update(published_at=timezone.now())

    translation = (
        Translation.objects.filter(product=instance, locale='fr').first()
        or Translation.objects.filter(product=instance).first()
    )
    if translation is None:
        return

    # Import local pour éviter les imports circulaires au démarrage
    from app.models import Product, Category

    # Famille → Catégorie (mapping naïf par nom : on prend ou crée la catégorie portant le nom de la famille)
    category, _ = Category.objects.get_or_create(name=instance.family.name)

    product = Product.objects.filter(pim_product=instance).first()
    if product is None:
        Product.objects.create(
            name=translation.name,
            category=category,
            global_quantity=0,
            pim_product=instance,
        )
    else:
        Product.objects.filter(pk=product.pk).update(
            name=translation.name,
            category=category,
        )
