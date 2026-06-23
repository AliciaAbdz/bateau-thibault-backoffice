from django.db import models
from django.conf import settings


class Family(models.Model):
    """Famille produit (ex: Poisson frais, Conserve). Déclare quels attributs sont attendus."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    attributes = models.ManyToManyField('Attribute', through='FamilyAttribute', related_name='families')

    def __str__(self):
        return self.name


class Attribute(models.Model):
    TYPE_TEXT = 'text'
    TYPE_NUMBER = 'number'
    TYPE_BOOL = 'bool'
    TYPE_SELECT = 'select'
    TYPE_CHOICES = [
        (TYPE_TEXT, 'Texte'),
        (TYPE_NUMBER, 'Nombre'),
        (TYPE_BOOL, 'Booléen'),
        (TYPE_SELECT, 'Liste de choix'),
    ]

    code = models.SlugField(max_length=64, unique=True)
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_TEXT)
    options = models.JSONField(default=list, blank=True, help_text="Pour type=select : liste des valeurs autorisées")
    is_localizable = models.BooleanField(default=False, help_text="True = une valeur par langue (ex: descriptif)")

    def __str__(self):
        return f"{self.label} ({self.type})"


class FamilyAttribute(models.Model):
    """Jointure Family ↔ Attribute avec is_required par famille."""
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=False)

    class Meta:
        unique_together = [('family', 'attribute')]


class PIMProduct(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_IN_REVIEW = 'in_review'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Brouillon'),
        (STATUS_IN_REVIEW, 'En validation'),
        (STATUS_PUBLISHED, 'Publié'),
        (STATUS_ARCHIVED, 'Archivé'),
    ]

    sku = models.CharField(max_length=64, unique=True)
    family = models.ForeignKey(Family, on_delete=models.PROTECT, related_name='products')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    completeness = models.PositiveSmallIntegerField(default=0, help_text="% attributs obligatoires remplis")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pim_products_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sku} [{self.status}]"

    def compute_completeness(self):
        """% d'attributs obligatoires de la famille effectivement remplis."""
        required_ids = list(FamilyAttribute.objects.filter(family=self.family, is_required=True).values_list('attribute_id', flat=True))
        total = len(required_ids)
        if total == 0:
            return 100
        filled = AttributeValue.objects.filter(product=self, attribute_id__in=required_ids).values('attribute_id').distinct().count()
        return int(round(100 * filled / total))


class AttributeValue(models.Model):
    """Valeur d'un attribut pour un produit donné, optionnellement localisée."""
    product = models.ForeignKey(PIMProduct, on_delete=models.CASCADE, related_name='attribute_values')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    locale = models.CharField(max_length=5, default='fr')
    value = models.TextField()

    class Meta:
        unique_together = [('product', 'attribute', 'locale')]


class Translation(models.Model):
    """Contenu marketing localisé : nom commercial + descriptif long."""
    product = models.ForeignKey(PIMProduct, on_delete=models.CASCADE, related_name='translations')
    locale = models.CharField(max_length=5)
    name = models.CharField(max_length=200)
    marketing_description = models.TextField(blank=True)

    class Meta:
        unique_together = [('product', 'locale')]

    def __str__(self):
        return f"{self.product.sku} [{self.locale}] {self.name}"


class Asset(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_PDF = 'pdf'
    TYPE_CHOICES = [
        (TYPE_IMAGE, 'Image'),
        (TYPE_VIDEO, 'Vidéo'),
        (TYPE_PDF, 'PDF'),
    ]

    product = models.ForeignKey(PIMProduct, on_delete=models.CASCADE, related_name='assets')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_IMAGE)
    url = models.URLField(max_length=500)
    position = models.PositiveSmallIntegerField(default=0)
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['position', 'id']
