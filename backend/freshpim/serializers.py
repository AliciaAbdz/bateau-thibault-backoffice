from rest_framework import serializers

from .models import (
    Family, Attribute, FamilyAttribute,
    PIMProduct, AttributeValue, Translation, Asset,
)


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'code', 'label', 'type', 'options', 'is_localizable']


class FamilyAttributeSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=Attribute.objects.all(), source='attribute', write_only=True
    )

    class Meta:
        model = FamilyAttribute
        fields = ['id', 'attribute', 'attribute_id', 'is_required']


class FamilySerializer(serializers.ModelSerializer):
    family_attributes = FamilyAttributeSerializer(source='familyattribute_set', many=True, read_only=True)

    class Meta:
        model = Family
        fields = ['id', 'name', 'description', 'family_attributes']


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ['id', 'locale', 'name', 'marketing_description']


class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_code = serializers.CharField(source='attribute.code', read_only=True)
    attribute_label = serializers.CharField(source='attribute.label', read_only=True)
    attribute_type = serializers.CharField(source='attribute.type', read_only=True)

    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute', 'attribute_code', 'attribute_label', 'attribute_type', 'locale', 'value']


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'type', 'url', 'position', 'alt_text']


class PIMProductListSerializer(serializers.ModelSerializer):
    """Vue allégée pour les listes."""
    family_name = serializers.CharField(source='family.name', read_only=True)
    name_fr = serializers.SerializerMethodField()

    class Meta:
        model = PIMProduct
        fields = ['id', 'sku', 'family', 'family_name', 'status', 'completeness',
                  'name_fr', 'created_at', 'updated_at', 'published_at']

    def get_name_fr(self, obj):
        translation = next(
            (t for t in obj.translations.all() if t.locale == 'fr'),
            None,
        )
        return translation.name if translation else None


class PIMProductDetailSerializer(serializers.ModelSerializer):
    """Vue détaillée nested : famille + traductions + valeurs d'attributs + assets."""
    family = FamilySerializer(read_only=True)
    family_id = serializers.PrimaryKeyRelatedField(
        queryset=Family.objects.all(), source='family', write_only=True
    )
    translations = TranslationSerializer(many=True, read_only=True)
    attribute_values = AttributeValueSerializer(many=True, read_only=True)
    assets = AssetSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = PIMProduct
        fields = ['id', 'sku', 'family', 'family_id', 'status', 'completeness',
                  'created_by', 'created_by_username',
                  'created_at', 'updated_at', 'published_at',
                  'translations', 'attribute_values', 'assets']
        read_only_fields = ['status', 'completeness', 'published_at',
                            'created_at', 'updated_at', 'created_by']
