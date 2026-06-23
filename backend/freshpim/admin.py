from django.contrib import admin

from .models import (
    Family, Attribute, FamilyAttribute,
    PIMProduct, AttributeValue, Translation, Asset,
)


class FamilyAttributeInline(admin.TabularInline):
    model = FamilyAttribute
    extra = 1


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    inlines = [FamilyAttributeInline]


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'label', 'type', 'is_localizable')
    list_filter = ('type', 'is_localizable')
    search_fields = ('code', 'label')


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 1


class AssetInline(admin.TabularInline):
    model = Asset
    extra = 1


@admin.register(PIMProduct)
class PIMProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'family', 'status', 'completeness', 'updated_at')
    list_filter = ('status', 'family')
    search_fields = ('sku',)
    readonly_fields = ('completeness', 'created_at', 'updated_at', 'published_at')
    inlines = [TranslationInline, AttributeValueInline, AssetInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        new_completeness = obj.compute_completeness()
        if new_completeness != obj.completeness:
            PIMProduct.objects.filter(pk=obj.pk).update(completeness=new_completeness)


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'locale', 'name')
    list_filter = ('locale',)
    search_fields = ('name', 'product__sku')


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'type', 'position', 'url')
    list_filter = ('type',)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'attribute', 'locale', 'value')
    list_filter = ('locale', 'attribute')
