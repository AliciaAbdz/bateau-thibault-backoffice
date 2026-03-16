from django.core.management.base import BaseCommand
from app.models import (
    Utilisateur, Category, Product, Manufacturer,
    ManufacturerArticle, Retailer, RetailerArticle, Purchase, Sale
)
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed la base de données avec des jeux de données'

    def handle(self, *args, **options):
        self.stdout.write('Suppression des anciennes données...')
        Sale.objects.all().delete()
        Purchase.objects.all().delete()
        RetailerArticle.objects.all().delete()
        ManufacturerArticle.objects.all().delete()
        Manufacturer.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Utilisateur.objects.all().delete()
        Retailer.objects.all().delete()

        # --- RETAILERS (créés en premier car Utilisateur a une FK vers Retailer) ---
        self.stdout.write('Création des points relais...')
        retailers_data = [
            ('FreshPoint Brest', '25 Rue de Siam, 29200 Brest'),
            ('FreshPoint Lorient', '12 Cours de Chazelles, 56100 Lorient'),
            ('FreshPoint Rennes', '8 Place de la Mairie, 35000 Rennes'),
            ('FreshPoint Nantes', '45 Rue Crébillon, 44000 Nantes'),
            ('FreshPoint Saint-Malo', '3 Intra-Muros, 35400 Saint-Malo'),
            ('FreshPoint Quimper', '17 Rue Kéréon, 29000 Quimper'),
            ('FreshPoint Vannes', '22 Place des Lices, 56000 Vannes'),
            ('FreshPoint La Rochelle', '6 Rue du Palais, 17000 La Rochelle'),
            ('FreshPoint Bordeaux', '50 Cours de l\'Intendance, 33000 Bordeaux'),
            ('FreshPoint Paris 5e', '14 Rue Mouffetard, 75005 Paris'),
            ('FreshPoint Paris 16e', '88 Avenue Victor Hugo, 75016 Paris'),
            ('FreshPoint Lyon', '30 Rue Mercière, 69002 Lyon'),
            ('FreshPoint Marseille', '65 La Canebière, 13001 Marseille'),
            ('FreshPoint Toulouse', '18 Rue Alsace-Lorraine, 31000 Toulouse'),
            ('FreshPoint Nice', '10 Cours Saleya, 06300 Nice'),
        ]
        retailers = []
        for name, address in retailers_data:
            r = Retailer.objects.create(name=name, address=address)
            retailers.append(r)

        self.stdout.write(f'  -> {len(retailers)} points relais créés')

        # --- UTILISATEURS (plusieurs par retailer) ---
        self.stdout.write('Création des utilisateurs...')
        users = []
        users_data = [
            # FreshPoint Brest (index 0) - 1 admin + 3 users
            {'name': 'ERNANDES', 'first_name': 'Flavio', 'role': 'ROLE_ADMIN', 'email': 'flavio.ernandes@freshpilot.com', 'retailer_idx': 0},
            {'name': 'LALAURIE', 'first_name': 'Jennifer', 'role': 'ROLE_USER', 'email': 'jennifer.lalaurie@freshpilot.com', 'retailer_idx': 0},
            {'name': 'FARINGA', 'first_name': 'Ahmad', 'role': 'ROLE_USER', 'email': 'ahmad.faringa@freshpilot.com', 'retailer_idx': 0},
            {'name': 'KHOURY', 'first_name': 'Layla', 'role': 'ROLE_USER', 'email': 'layla.khoury@freshpilot.com', 'retailer_idx': 0},
            {'name': 'BRIAC', 'first_name': 'Hector', 'role': 'ROLE_USER', 'email': 'hector.briac@freshpilot.com', 'retailer_idx': 0},

            # FreshPoint Lorient (index 1) - 1 admin + 2 users
            {'name': 'COZZO', 'first_name': 'Sivan', 'role': 'ROLE_ADMIN', 'email': 'sivan.cozzo@freshpilot.com', 'retailer_idx': 1},
            {'name': 'ABDOULAZIZE', 'first_name': 'Alicia', 'role': 'ROLE_ADMIN', 'email': 'alicia.abdoulazize@freshpilot.com', 'retailer_idx': 1},
            {'name': 'DUPONT', 'first_name': 'Marie', 'role': 'ROLE_USER', 'email': 'marie.dupont@freshpilot.com', 'retailer_idx': 1},

            # FreshPoint Rennes (index 2) - 1 admin + 2 users
            {'name': 'MARTIN', 'first_name': 'Lucas', 'role': 'ROLE_ADMIN', 'email': 'lucas.martin@freshpilot.com', 'retailer_idx': 2},
            {'name': 'BERNARD', 'first_name': 'Sophie', 'role': 'ROLE_USER', 'email': 'sophie.bernard@freshpilot.com', 'retailer_idx': 2},
            {'name': 'PETIT', 'first_name': 'Thomas', 'role': 'ROLE_USER', 'email': 'thomas.petit@freshpilot.com', 'retailer_idx': 2},

            # FreshPoint Nantes (index 3) - 1 admin + 1 user
            {'name': 'MOREAU', 'first_name': 'Camille', 'role': 'ROLE_ADMIN', 'email': 'camille.moreau@freshpilot.com', 'retailer_idx': 3},
            {'name': 'GARCIA', 'first_name': 'Pablo', 'role': 'ROLE_USER', 'email': 'pablo.garcia@freshpilot.com', 'retailer_idx': 3},

            # FreshPoint Saint-Malo (index 4) - 1 admin + 1 user
            {'name': 'LEFEVRE', 'first_name': 'Julie', 'role': 'ROLE_ADMIN', 'email': 'julie.lefevre@freshpilot.com', 'retailer_idx': 4},
            {'name': 'ROUX', 'first_name': 'Antoine', 'role': 'ROLE_USER', 'email': 'antoine.roux@freshpilot.com', 'retailer_idx': 4},

            # FreshPoint Quimper (index 5) - 1 admin + 2 users
            {'name': 'LECLERC', 'first_name': 'Hugo', 'role': 'ROLE_ADMIN', 'email': 'hugo.leclerc@freshpilot.com', 'retailer_idx': 5},
            {'name': 'GIRARD', 'first_name': 'Emma', 'role': 'ROLE_USER', 'email': 'emma.girard@freshpilot.com', 'retailer_idx': 5},
            {'name': 'BONNET', 'first_name': 'Léo', 'role': 'ROLE_USER', 'email': 'leo.bonnet@freshpilot.com', 'retailer_idx': 5},

            # FreshPoint Vannes (index 6) - 1 admin + 2 users
            {'name': 'LAMBERT', 'first_name': 'Chloé', 'role': 'ROLE_ADMIN', 'email': 'chloe.lambert@freshpilot.com', 'retailer_idx': 6},
            {'name': 'FONTAINE', 'first_name': 'Nathan', 'role': 'ROLE_USER', 'email': 'nathan.fontaine@freshpilot.com', 'retailer_idx': 6},
            {'name': 'ROUSSEAU', 'first_name': 'Inès', 'role': 'ROLE_USER', 'email': 'ines.rousseau@freshpilot.com', 'retailer_idx': 6},

            # FreshPoint La Rochelle (index 7) - 1 admin + 1 user
            {'name': 'VINCENT', 'first_name': 'Raphaël', 'role': 'ROLE_ADMIN', 'email': 'raphael.vincent@freshpilot.com', 'retailer_idx': 7},
            {'name': 'MULLER', 'first_name': 'Léa', 'role': 'ROLE_USER', 'email': 'lea.muller@freshpilot.com', 'retailer_idx': 7},

            # FreshPoint Bordeaux (index 8) - 1 admin + 3 users
            {'name': 'FOURNIER', 'first_name': 'Gabriel', 'role': 'ROLE_ADMIN', 'email': 'gabriel.fournier@freshpilot.com', 'retailer_idx': 8},
            {'name': 'MERCIER', 'first_name': 'Manon', 'role': 'ROLE_USER', 'email': 'manon.mercier@freshpilot.com', 'retailer_idx': 8},
            {'name': 'BLANC', 'first_name': 'Louis', 'role': 'ROLE_USER', 'email': 'louis.blanc@freshpilot.com', 'retailer_idx': 8},
            {'name': 'GUERIN', 'first_name': 'Jade', 'role': 'ROLE_USER', 'email': 'jade.guerin@freshpilot.com', 'retailer_idx': 8},

            # FreshPoint Paris 5e (index 9) - 1 admin + 2 users
            {'name': 'HENRY', 'first_name': 'Adam', 'role': 'ROLE_ADMIN', 'email': 'adam.henry@freshpilot.com', 'retailer_idx': 9},
            {'name': 'MASSON', 'first_name': 'Lina', 'role': 'ROLE_USER', 'email': 'lina.masson@freshpilot.com', 'retailer_idx': 9},
            {'name': 'ROBIN', 'first_name': 'Ethan', 'role': 'ROLE_USER', 'email': 'ethan.robin@freshpilot.com', 'retailer_idx': 9},

            # FreshPoint Paris 16e (index 10) - 1 admin + 1 user
            {'name': 'LEMOINE', 'first_name': 'Alice', 'role': 'ROLE_ADMIN', 'email': 'alice.lemoine@freshpilot.com', 'retailer_idx': 10},
            {'name': 'CHEVALIER', 'first_name': 'Arthur', 'role': 'ROLE_USER', 'email': 'arthur.chevalier@freshpilot.com', 'retailer_idx': 10},

            # FreshPoint Lyon (index 11) - 1 admin + 2 users
            {'name': 'FAURE', 'first_name': 'Rose', 'role': 'ROLE_ADMIN', 'email': 'rose.faure@freshpilot.com', 'retailer_idx': 11},
            {'name': 'GAUTHIER', 'first_name': 'Sacha', 'role': 'ROLE_USER', 'email': 'sacha.gauthier@freshpilot.com', 'retailer_idx': 11},
            {'name': 'PERRIN', 'first_name': 'Ambre', 'role': 'ROLE_USER', 'email': 'ambre.perrin@freshpilot.com', 'retailer_idx': 11},

            # FreshPoint Marseille (index 12) - 1 admin + 2 users
            {'name': 'MOREL', 'first_name': 'Théo', 'role': 'ROLE_ADMIN', 'email': 'theo.morel@freshpilot.com', 'retailer_idx': 12},
            {'name': 'SIMON', 'first_name': 'Eva', 'role': 'ROLE_USER', 'email': 'eva.simon@freshpilot.com', 'retailer_idx': 12},
            {'name': 'LAURENT', 'first_name': 'Noé', 'role': 'ROLE_USER', 'email': 'noe.laurent@freshpilot.com', 'retailer_idx': 12},

            # FreshPoint Toulouse (index 13) - 1 admin + 1 user
            {'name': 'MICHEL', 'first_name': 'Mila', 'role': 'ROLE_ADMIN', 'email': 'mila.michel@freshpilot.com', 'retailer_idx': 13},
            {'name': 'DAVID', 'first_name': 'Jules', 'role': 'ROLE_USER', 'email': 'jules.david@freshpilot.com', 'retailer_idx': 13},

            # FreshPoint Nice (index 14) - 1 admin + 2 users
            {'name': 'BERTRAND', 'first_name': 'Lola', 'role': 'ROLE_ADMIN', 'email': 'lola.bertrand@freshpilot.com', 'retailer_idx': 14},
            {'name': 'RIVIERE', 'first_name': 'Tom', 'role': 'ROLE_USER', 'email': 'tom.riviere@freshpilot.com', 'retailer_idx': 14},
            {'name': 'ARNAUD', 'first_name': 'Clara', 'role': 'ROLE_USER', 'email': 'clara.arnaud@freshpilot.com', 'retailer_idx': 14},
        ]
        for u in users_data:
            username = f"{u['first_name'].lower()}.{u['name'].lower()}"
            user = Utilisateur.objects.create_user(
                username=username,
                last_name=u['name'],
                first_name=u['first_name'],
                role=u['role'],
                email=u['email'],
                password='freshpilot2026',
                retailer=retailers[u['retailer_idx']],
            )
            users.append(user)

        self.stdout.write(f'  -> {len(users)} utilisateurs créés')

        # --- CATEGORIES ---
        self.stdout.write('Création des catégories...')
        categories_data = [
            'Poissons', 'Crustacés', 'Coquillages', 'Fruits de mer',
            'Algues', 'Céphalopodes', 'Poissons fumés', 'Conserves',
            'Surgelés', 'Sauces et accompagnements',
        ]
        categories = []
        for name in categories_data:
            cat = Category.objects.create(name=name)
            categories.append(cat)

        self.stdout.write(f'  -> {len(categories)} catégories créées')

        # --- PRODUCTS ---
        self.stdout.write('Création des produits...')
        products_data = [
            # Poissons
            ('Bar de ligne', 0, 250), ('Daurade royale', 0, 180), ('Sole', 0, 120),
            ('Cabillaud', 0, 300), ('Merlu', 0, 200), ('Turbot', 0, 90),
            ('Saint-Pierre', 0, 75), ('Loup de mer', 0, 150), ('Rouget barbet', 0, 100),
            ('Maquereau', 0, 400), ('Sardine', 0, 500), ('Thon rouge', 0, 60),
            ('Saumon atlantique', 0, 350), ('Truite arc-en-ciel', 0, 220),
            # Crustacés
            ('Homard breton', 1, 80), ('Langoustine', 1, 150), ('Crabe tourteau', 1, 120),
            ('Crevette rose', 1, 300), ('Araignée de mer', 1, 70), ('Étrille', 1, 90),
            ('Langoustine vivante', 1, 60), ('Gambas', 1, 200),
            # Coquillages
            ('Huître creuse n°3', 2, 500), ('Huître plate Belon', 2, 200),
            ('Moule de bouchot', 2, 800), ('Saint-Jacques', 2, 150),
            ('Palourde', 2, 180), ('Coque', 2, 250), ('Bulot', 2, 300),
            ('Praire', 2, 120),
            # Fruits de mer
            ('Plateau fruits de mer 2p', 3, 40), ('Plateau fruits de mer 4p', 3, 30),
            ('Plateau royal 6p', 3, 20), ('Assortiment crevettes', 3, 100),
            # Algues
            ('Wakamé', 4, 50), ('Nori', 4, 80), ('Dulse', 4, 40),
            ('Laitue de mer', 4, 60), ('Spiruline fraîche', 4, 30),
            # Céphalopodes
            ('Poulpe', 5, 100), ('Calamar', 5, 200), ('Seiche', 5, 150),
            ('Encornet', 5, 180), ('Petit poulpe', 5, 90),
            # Poissons fumés
            ('Saumon fumé', 6, 250), ('Truite fumée', 6, 150),
            ('Haddock', 6, 100), ('Maquereau fumé', 6, 120),
            ('Espadon fumé', 6, 60),
            # Conserves
            ('Sardines à l\'huile d\'olive', 7, 400), ('Thon en conserve', 7, 500),
            ('Rillettes de saumon', 7, 200), ('Soupe de poisson', 7, 300),
            ('Bisque de homard', 7, 150), ('Anchois marinés', 7, 180),
            # Surgelés
            ('Filets de cabillaud surgelés', 8, 300), ('Crevettes surgelées', 8, 400),
            ('Calamars surgelés', 8, 250), ('Moules surgelées', 8, 350),
            ('Pavé de saumon surgelé', 8, 280),
            # Sauces
            ('Sauce tartare', 9, 200), ('Beurre blanc', 9, 150),
            ('Aïoli', 9, 180), ('Rouille', 9, 120), ('Mayonnaise maison', 9, 250),
        ]
        products = []
        for name, cat_idx, qty in products_data:
            prod = Product.objects.create(
                name=name,
                category=categories[cat_idx],
                global_quantity=qty,
            )
            products.append(prod)

        self.stdout.write(f'  -> {len(products)} produits créés')

        # --- MANUFACTURERS ---
        self.stdout.write('Création des fournisseurs...')
        manufacturers_data = [
            ('Pêcheries Bretonnes', '12 Quai du Port, 29200 Brest'),
            ('Marée Fraîche SARL', '45 Rue de la Criée, 56100 Lorient'),
            ('Atlantique Seafood', '8 Avenue du Littoral, 44600 Saint-Nazaire'),
            ('Côtes d\'Armor Pêche', '3 Rue du Phare, 22000 Saint-Brieuc'),
            ('Normandie Coquillages', '67 Boulevard Maritime, 50400 Granville'),
            ('Méditerranée Import', '15 Port de Sète, 34200 Sète'),
            ('Océan Pacifique Trading', '22 Quai des Pêcheurs, 64600 Anglet'),
            ('Fumoir du Nord', '4 Rue des Artisans, 62200 Boulogne-sur-Mer'),
            ('Les Viviers de l\'Île', '1 Port de la Pointe, 56360 Belle-Île'),
            ('Conserverie Artisanale', '9 Zone Artisanale, 29900 Concarneau'),
            ('Algues de Bretagne', '18 Chemin Côtier, 29680 Roscoff'),
            ('La Criée du Guilvinec', '5 Port du Guilvinec, 29730 Guilvinec'),
            ('Mareyeur Dupont', '33 Quai Gambetta, 62200 Boulogne-sur-Mer'),
            ('Ostréiculteur Morvan', '7 Parc à Huîtres, 56470 La Trinité-sur-Mer'),
            ('Pêche Durable SA', '21 Rue Écoresponsable, 17000 La Rochelle'),
        ]
        manufacturers = []
        for name, address in manufacturers_data:
            m = Manufacturer.objects.create(name=name, address=address)
            manufacturers.append(m)

        self.stdout.write(f'  -> {len(manufacturers)} fournisseurs créés')

        # --- MANUFACTURER ARTICLES ---
        self.stdout.write('Création des articles fournisseurs...')
        units = ['kg', 'pièce', 'lot', 'barq.', 'dz']
        comments_list = [
            'Produit frais du jour', 'Qualité premium', 'Pêche durable MSC',
            'Label Rouge', 'Origine certifiée', 'Livraison sous 24h',
            'Stock limité', 'Nouvelle récolte', 'Produit de saison',
            'Approvisionnement régulier', 'Calibre exceptionnel',
            'Traçabilité complète', 'Pêche artisanale', 'Bio certifié',
            'Lot promotionnel', 'Fin de saison', 'Arrivage spécial',
        ]
        manufacturer_articles = []
        for prod in products:
            nb_articles = random.randint(1, 3)
            for _ in range(nb_articles):
                ma = ManufacturerArticle.objects.create(
                    unit=random.choice(units),
                    availability=random.choice([True, True, True, False]),
                    sales=random.randint(0, 500),
                    comments=random.choice(comments_list),
                    prod=prod,
                    manufacturer=random.choice(manufacturers),
                )
                manufacturer_articles.append(ma)

        self.stdout.write(f'  -> {len(manufacturer_articles)} articles fournisseurs créés')

        # --- RETAILER ARTICLES ---
        self.stdout.write('Création des articles en point relais...')
        retailer_articles = []
        for ma in manufacturer_articles:
            nb_retailers = random.randint(1, 4)
            chosen_retailers = random.sample(retailers, min(nb_retailers, len(retailers)))
            for retailer in chosen_retailers:
                ra = RetailerArticle.objects.create(
                    discount=random.choice([0, 0, 0, 5, 10, 15, 20, 25, 30]),
                    image='',
                    unit_price=random.randint(3, 85),
                    quantity=random.randint(0, 200),
                    is_archived=random.choice([False, False, False, False, True]),
                    tig=ma,
                    retail=retailer,
                )
                retailer_articles.append(ra)

        self.stdout.write(f'  -> {len(retailer_articles)} articles point relais créés')

        # --- PURCHASES ---
        self.stdout.write('Création des achats...')
        purchases = []
        for _ in range(200):
            ra = random.choice(retailer_articles)
            qty = random.randint(1, 50)
            p = Purchase.objects.create(
                total=ra.unit_price * qty,
                quantity=qty,
                retailer_article=ra,
            )
            purchases.append(p)

        self.stdout.write(f'  -> {len(purchases)} achats créés')

        # --- SALES ---
        self.stdout.write('Création des ventes...')
        sales = []
        for _ in range(300):
            ra = random.choice(retailer_articles)
            qty = random.randint(1, 30)
            price = ra.unit_price
            if ra.discount > 0:
                price = int(price * (100 - ra.discount) / 100)
            s = Sale.objects.create(
                total=price * qty,
                quantity=qty,
                retailer_article=ra,
            )
            sales.append(s)

        self.stdout.write(f'  -> {len(sales)} ventes créées')

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed terminé avec succès !\n'
            f'  - {len(users)} utilisateurs\n'
            f'  - {len(categories)} catégories\n'
            f'  - {len(products)} produits\n'
            f'  - {len(manufacturers)} fournisseurs\n'
            f'  - {len(manufacturer_articles)} articles fournisseurs\n'
            f'  - {len(retailers)} points relais\n'
            f'  - {len(retailer_articles)} articles point relais\n'
            f'  - {len(purchases)} achats\n'
            f'  - {len(sales)} ventes'
        ))
