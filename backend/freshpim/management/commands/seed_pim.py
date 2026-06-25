from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from app.models import Utilisateur, Manufacturer
from freshpim.models import (
    Family, Attribute, FamilyAttribute,
    PIMProduct, AttributeValue, Translation, Asset,
)


class Command(BaseCommand):
    help = "Seed FreshPIM : 1 famille Poisson + 5 attributs + 3 produits PIM (draft / in_review / published)."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Nettoyage FreshPIM...")
        Asset.objects.all().delete()
        AttributeValue.objects.all().delete()
        Translation.objects.all().delete()
        PIMProduct.objects.all().delete()
        FamilyAttribute.objects.all().delete()
        Attribute.objects.all().delete()
        Family.objects.all().delete()

        # ---- Comptes fournisseurs liés à des Manufacturers existants ----
        self.stdout.write("Liaison comptes fournisseurs ↔ Manufacturers...")
        manufacturers = list(Manufacturer.objects.all()[:2])
        if len(manufacturers) < 2:
            self.stdout.write(self.style.WARNING("Lance d'abord `python manage.py seed` (app) pour avoir des Manufacturers."))
            return

        for m in manufacturers:
            if not m.email:
                m.email = f"contact@{m.name.lower().replace(' ', '').replace(chr(39), '')[:20]}.fr"
                m.save(update_fields=['email'])

        manufacturer_users = []
        for idx, m in enumerate(manufacturers):
            username = f"manufacturer{idx + 1}"
            user, created = Utilisateur.objects.update_or_create(
                username=username,
                defaults={
                    'first_name': m.name.split()[0][:30],
                    'last_name': 'Manufacturer',
                    'email': m.email or f'{username}@freshpim.com',
                    'role': Utilisateur.ROLE_MANUFACTURER,
                    'manufacturer': m,
                },
            )
            if created:
                user.set_password('freshpilot2026')
                user.save()
            manufacturer_users.append(user)

        # ---- Compte admin PIM ----
        pim_admin, created = Utilisateur.objects.update_or_create(
            username='pim.admin',
            defaults={
                'first_name': 'PIM',
                'last_name': 'Admin',
                'email': 'pim.admin@freshpim.com',
                'role': Utilisateur.ROLE_PIM_ADMIN,
            },
        )
        if created:
            pim_admin.set_password('freshpilot2026')
            pim_admin.save()

        # ---- Catalogue d'attributs (partagés entre familles) ----
        self.stdout.write("Création du catalogue d'attributs...")
        attrs_catalog = [
            # code, label, type, options, is_localizable
            ('calibre', 'Calibre (g)', Attribute.TYPE_NUMBER, [], False),
            ('zone_peche', 'Zone de pêche FAO', Attribute.TYPE_TEXT, [], False),
            ('label', 'Label qualité', Attribute.TYPE_SELECT,
                ['Aucun', 'MSC', 'Label Rouge', 'Bio', 'AOP', 'Pêche Durable'], False),
            ('methode_capture', 'Méthode de capture', Attribute.TYPE_SELECT,
                ['Ligne', 'Filet', 'Casier', 'Chalut', 'Plongée'], False),
            ('description_courte', 'Description courte', Attribute.TYPE_TEXT, [], True),
            ('origine', 'Origine', Attribute.TYPE_TEXT, [], False),
            ('elevage_sauvage', 'Élevage / Sauvage', Attribute.TYPE_SELECT,
                ['Sauvage', 'Élevage', 'Bouchot', 'Parc'], False),
            ('dlc_jours', 'DLC (jours après réception)', Attribute.TYPE_NUMBER, [], False),
            ('contenance_g', 'Contenance nette (g)', Attribute.TYPE_NUMBER, [], False),
            ('emballage', 'Emballage', Attribute.TYPE_SELECT,
                ['Boîte métal', 'Bocal verre', 'Sachet plastique', 'Carton'], False),
            ('ingredients', 'Ingrédients', Attribute.TYPE_TEXT, [], True),
            ('bio', 'Bio', Attribute.TYPE_BOOL, [], False),
            # --- Attributs « Eau » (collent à une étiquette de bouteille) ---
            ('marque', 'Marque', Attribute.TYPE_TEXT, [], False),
            ('type_eau', 'Type d\'eau', Attribute.TYPE_SELECT,
                ['Eau de source', 'Eau minérale naturelle', 'Eau de table', 'Eau gazeuse'], False),
            ('contenance_l', 'Contenance (L)', Attribute.TYPE_NUMBER, [], False),
            ('residu_sec', 'Résidu sec à 180°C (mg/L)', Attribute.TYPE_NUMBER, [], False),
            ('ph', 'pH', Attribute.TYPE_NUMBER, [], False),
            ('calcium', 'Calcium (mg/L)', Attribute.TYPE_NUMBER, [], False),
            ('sodium', 'Sodium (mg/L)', Attribute.TYPE_NUMBER, [], False),
            # --- Attributs « Soda » (collent à une canette/bouteille) ---
            ('type_boisson', 'Type de boisson', Attribute.TYPE_SELECT,
                ['Cola', 'Limonade', 'Tonic', 'Soda aux fruits', 'Thé glacé', 'Énergisant'], False),
            ('contenance_ml', 'Contenance (mL)', Attribute.TYPE_NUMBER, [], False),
            ('petillant', 'Pétillant', Attribute.TYPE_BOOL, [], False),
            ('calories', 'Calories (par portion)', Attribute.TYPE_NUMBER, [], False),
            ('sucres_g', 'Sucres (g)', Attribute.TYPE_NUMBER, [], False),
            ('cafeine_mg', 'Caféine (mg)', Attribute.TYPE_NUMBER, [], False),
        ]
        attrs = {}
        for code, label, atype, options, is_localizable in attrs_catalog:
            attrs[code] = Attribute.objects.create(
                code=code, label=label, type=atype,
                options=options, is_localizable=is_localizable,
            )

        # ---- Familles (chacune réutilise un sous-ensemble du catalogue) ----
        self.stdout.write("Création des familles...")
        families_def = [
            # name, description, [(attr_code, is_required), ...]
            ('Poisson frais', 'Poisson entier ou en filet, frais, non transformé.', [
                ('calibre', True), ('zone_peche', True), ('methode_capture', True),
                ('label', False), ('description_courte', False),
            ]),
            ('Crustacés', 'Homards, langoustines, crevettes — vivants ou cuits.', [
                ('calibre', True), ('zone_peche', True), ('methode_capture', False),
                ('label', False), ('elevage_sauvage', True),
            ]),
            ('Coquillages', 'Huîtres, moules, palourdes, Saint-Jacques.', [
                ('calibre', False), ('origine', True), ('elevage_sauvage', True),
                ('label', False), ('description_courte', False),
            ]),
            ('Conserve', 'Produits de la mer en conserve, longue conservation.', [
                ('contenance_g', True), ('emballage', True), ('dlc_jours', True),
                ('ingredients', True), ('bio', False), ('origine', False),
            ]),
            ('Eau', 'Eau embouteillée (source, minérale). Sert à tester la reconnaissance d\'étiquette.', [
                ('marque', True), ('type_eau', True), ('contenance_l', True), ('origine', True),
                ('residu_sec', False), ('ph', False), ('calcium', False), ('sodium', False),
            ]),
            ('Soda', 'Boisson gazeuse sucrée. Sert à tester la reconnaissance d\'étiquette.', [
                ('marque', True), ('type_boisson', True), ('contenance_ml', True), ('petillant', False),
                ('calories', False), ('sucres_g', False), ('cafeine_mg', False), ('ingredients', False),
            ]),
        ]
        families = {}
        for name, description, attr_links in families_def:
            f = Family.objects.create(name=name, description=description)
            families[name] = f
            for code, is_required in attr_links:
                FamilyAttribute.objects.create(family=f, attribute=attrs[code], is_required=is_required)

        # Famille principale pour les anciens produits de démo
        family = families['Poisson frais']

        # ---- 3 PIMProduct dans 3 états ----
        self.stdout.write("Création des 3 PIMProduct (draft / in_review / published)...")

        # 1. DRAFT — Pêcheries Bretonnes vient juste de commencer
        p_draft = PIMProduct.objects.create(
            sku='PIM-BAR-001', family=family,
            status=PIMProduct.STATUS_DRAFT,
            created_by=manufacturer_users[0],
        )
        Translation.objects.create(product=p_draft, locale='fr', name='Bar de ligne (brouillon)')
        AttributeValue.objects.create(product=p_draft, attribute=attrs['calibre'], locale='-', value='800')
        p_draft.completeness = p_draft.compute_completeness()
        p_draft.save(update_fields=['completeness'])

        # 2. IN_REVIEW — soumis pour validation, presque complet
        p_review = PIMProduct.objects.create(
            sku='PIM-CAB-002', family=family,
            status=PIMProduct.STATUS_IN_REVIEW,
            created_by=manufacturer_users[1],
        )
        Translation.objects.create(product=p_review, locale='fr', name='Cabillaud entier',
                                   marketing_description='Cabillaud sauvage de l\'Atlantique Nord, chair ferme et délicate.')
        Translation.objects.create(product=p_review, locale='en', name='Whole cod',
                                   marketing_description='Wild Atlantic cod, firm and delicate flesh.')
        AttributeValue.objects.create(product=p_review, attribute=attrs['calibre'], locale='-', value='2500')
        AttributeValue.objects.create(product=p_review, attribute=attrs['zone_peche'], locale='-', value='FAO 27')
        AttributeValue.objects.create(product=p_review, attribute=attrs['methode_capture'], locale='-', value='Ligne')
        AttributeValue.objects.create(product=p_review, attribute=attrs['label'], locale='-', value='MSC')
        Asset.objects.create(product=p_review, type=Asset.TYPE_IMAGE,
                             url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Gadus_morhua_Cod-2-Atlanterhavsparken-Norway.JPG/640px-Gadus_morhua_Cod-2-Atlanterhavsparken-Norway.JPG',
                             alt_text='Cabillaud entier', position=0)
        p_review.completeness = p_review.compute_completeness()
        p_review.save(update_fields=['completeness'])

        # 3. PUBLISHED — fiche complète, déclenche la sync vers FreshPilot
        p_pub = PIMProduct.objects.create(
            sku='PIM-DAU-003', family=family,
            status=PIMProduct.STATUS_DRAFT,  # créé en draft pour passer en published après remplissage
            created_by=manufacturer_users[0],
        )
        Translation.objects.create(product=p_pub, locale='fr', name='Daurade royale sauvage',
                                   marketing_description='Daurade royale de Méditerranée pêchée à la ligne. Chair noble et iodée.')
        Translation.objects.create(product=p_pub, locale='en', name='Wild gilthead seabream',
                                   marketing_description='Mediterranean wild gilthead seabream, line-caught.')
        AttributeValue.objects.create(product=p_pub, attribute=attrs['calibre'], locale='-', value='600')
        AttributeValue.objects.create(product=p_pub, attribute=attrs['zone_peche'], locale='-', value='FAO 37')
        AttributeValue.objects.create(product=p_pub, attribute=attrs['methode_capture'], locale='-', value='Ligne')
        AttributeValue.objects.create(product=p_pub, attribute=attrs['label'], locale='-', value='Label Rouge')
        Asset.objects.create(product=p_pub, type=Asset.TYPE_IMAGE,
                             url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Sparus_aurata_Sardinia.jpg/640px-Sparus_aurata_Sardinia.jpg',
                             alt_text='Daurade royale', position=0)
        # Passage en published → déclenche le signal sync_to_freshpilot
        p_pub.status = PIMProduct.STATUS_PUBLISHED
        p_pub.published_at = timezone.now()
        p_pub.completeness = p_pub.compute_completeness()
        p_pub.save()

        # ---- Produits dans les autres familles (montre que le formulaire d'attributs s'adapte) ----
        self.stdout.write("Création de fiches dans les autres familles...")

        # Crustacés — DRAFT
        p_crust = PIMProduct.objects.create(
            sku='PIM-HOM-010', family=families['Crustacés'],
            status=PIMProduct.STATUS_DRAFT, created_by=manufacturer_users[0],
        )
        Translation.objects.create(product=p_crust, locale='fr', name='Homard bleu de Bretagne')
        AttributeValue.objects.create(product=p_crust, attribute=attrs['calibre'], locale='-', value='650')
        AttributeValue.objects.create(product=p_crust, attribute=attrs['zone_peche'], locale='-', value='FAO 27.7')
        AttributeValue.objects.create(product=p_crust, attribute=attrs['elevage_sauvage'], locale='-', value='Sauvage')
        p_crust.completeness = p_crust.compute_completeness()
        p_crust.save(update_fields=['completeness'])

        # Coquillages — IN_REVIEW
        p_coq = PIMProduct.objects.create(
            sku='PIM-HUI-011', family=families['Coquillages'],
            status=PIMProduct.STATUS_IN_REVIEW, created_by=manufacturer_users[1],
        )
        Translation.objects.create(product=p_coq, locale='fr', name='Huître creuse Marennes-Oléron n°3',
                                   marketing_description='Huître affinée en claire, chair iodée et croquante.')
        AttributeValue.objects.create(product=p_coq, attribute=attrs['origine'], locale='-', value='Marennes-Oléron')
        AttributeValue.objects.create(product=p_coq, attribute=attrs['elevage_sauvage'], locale='-', value='Parc')
        AttributeValue.objects.create(product=p_coq, attribute=attrs['label'], locale='-', value='AOP')
        p_coq.completeness = p_coq.compute_completeness()
        p_coq.save(update_fields=['completeness'])

        # Conserve — PUBLISHED (sync FreshPilot)
        p_conv = PIMProduct.objects.create(
            sku='PIM-SAR-020', family=families['Conserve'],
            status=PIMProduct.STATUS_DRAFT, created_by=manufacturer_users[0],
        )
        Translation.objects.create(product=p_conv, locale='fr', name='Sardines à l\'huile d\'olive bio',
                                   marketing_description='Sardines bretonnes pêchées à la bolinche, à l\'huile d\'olive vierge bio.')
        Translation.objects.create(product=p_conv, locale='en', name='Organic sardines in olive oil',
                                   marketing_description='Breton sardines line-caught, in organic virgin olive oil.')
        AttributeValue.objects.create(product=p_conv, attribute=attrs['contenance_g'], locale='-', value='115')
        AttributeValue.objects.create(product=p_conv, attribute=attrs['emballage'], locale='-', value='Boîte métal')
        AttributeValue.objects.create(product=p_conv, attribute=attrs['dlc_jours'], locale='-', value='1095')
        AttributeValue.objects.create(product=p_conv, attribute=attrs['ingredients'], locale='fr',
                                       value='Sardines, huile d\'olive vierge biologique, sel.')
        AttributeValue.objects.create(product=p_conv, attribute=attrs['ingredients'], locale='en',
                                       value='Sardines, organic virgin olive oil, salt.')
        AttributeValue.objects.create(product=p_conv, attribute=attrs['bio'], locale='-', value='true')
        Asset.objects.create(product=p_conv, type=Asset.TYPE_IMAGE,
                             url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Sardines_in_olive_oil.jpg/640px-Sardines_in_olive_oil.jpg',
                             alt_text='Sardines à l\'huile d\'olive', position=0)
        p_conv.status = PIMProduct.STATUS_PUBLISHED
        p_conv.published_at = timezone.now()
        p_conv.completeness = p_conv.compute_completeness()
        p_conv.save()

        # Eau — DRAFT VIDE : sert à tester la reconnaissance d'étiquette
        # (importe demo/RECTIFY_*.jpg → les attributs se remplissent, la complétude grimpe)
        p_eau = PIMProduct.objects.create(
            sku='PIM-EAU-030', family=families['Eau'],
            status=PIMProduct.STATUS_DRAFT, created_by=manufacturer_users[0],
        )
        Translation.objects.create(product=p_eau, locale='fr', name='Eau à compléter (importer une étiquette)')
        p_eau.completeness = p_eau.compute_completeness()  # 0% : aucun attribut rempli
        p_eau.save(update_fields=['completeness'])

        # Soda — DRAFT VIDE : sert à tester la reconnaissance d'étiquette (demo/SODA_COCA_COLA.jpg)
        p_soda = PIMProduct.objects.create(
            sku='PIM-SOD-040', family=families['Soda'],
            status=PIMProduct.STATUS_DRAFT, created_by=manufacturer_users[0],
        )
        Translation.objects.create(product=p_soda, locale='fr', name='Soda à compléter (importer une étiquette)')
        p_soda.completeness = p_soda.compute_completeness()  # 0%
        p_soda.save(update_fields=['completeness'])

        self.stdout.write(self.style.SUCCESS(
            f"\nFreshPIM seed OK :\n"
            f"  - {len(families)} familles : {', '.join(families.keys())}\n"
            f"  - {len(attrs)} attributs partagés entre familles selon le gabarit\n"
            f"  - {len(manufacturer_users)} comptes fournisseurs (login: manufacturer1 / manufacturer2 — pwd: freshpilot2026)\n"
            f"  - 1 compte admin PIM (login: pim.admin — pwd: freshpilot2026)\n"
            f"  - 8 PIMProducts (dont 'Eau' + 'Soda' VIDES pour tester l'import d'étiquette) sur les {len(families)} familles\n"
        ))
