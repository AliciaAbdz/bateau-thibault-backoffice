import { Component, computed, signal } from '@angular/core';
import { RetailArticleDisplay, StockChange } from '../../../models/models';
import { ProductsService } from '../../../services/products/products.service';
import { ClientService } from '../../../services/client/client.service';
import { FormsModule } from '@angular/forms';

interface ArticleModification {
  quantity_change: number | null;
  is_expired: boolean;
}

interface PurchaseEntry {
  article_id: number;
  name: string;
  quantity: number;
  purchase_price: number | null;
}

@Component({
  selector: 'app-products',
  host: { class: 'flex flex-col flex-1' },
  imports: [FormsModule],
  templateUrl: './products.component.html',
  styleUrl: './products.component.css'
})
export class ProductsComponent {

  retailArticles = signal<RetailArticleDisplay[]>([]);
  selectedCategory = signal<string | null>(null);
  categories = computed(() => this.productService.getRetailerCategory(this.retailArticles()));
  filteredArticles = computed(() => {
    const selected = this.selectedCategory();
    if (!selected) return this.retailArticles();
    return this.retailArticles().filter(a => a.category === selected);
  });

  userId = 1; // TODO: récupérer du JWT

  // Modifications saisies par l'utilisateur (clé = article id)
  modifications: Record<number, ArticleModification> = {};

  // Popup prix d'achat
  showPurchaseModal = signal(false);
  purchaseEntries = signal<PurchaseEntry[]>([]);

  // Erreurs de validation
  errors: Record<number, string> = {};

  // Colonnes éditables ouvertes
  openColumns: Set<string> = new Set();
  newValues: Record<string, string[]> = {};

  constructor(
    private productService: ProductsService,
    private clientService: ClientService
  ) {}

  ngOnInit() {
    this.loadArticles();
  }

  loadArticles() {
    this.productService.getArticles(this.userId).subscribe(data => {
      this.retailArticles.set(data);
      const cats = this.categories();
      if (cats.length > 0 && !this.selectedCategory()) {
        this.selectedCategory.set(cats[0]);
      }
      // Initialiser les modifications vides pour chaque article
      this.modifications = {};
      data.forEach(a => {
        this.modifications[a.id] = { quantity_change: null, is_expired: false };
      });
    });
  }

  selectCategory(category: string) {
    this.selectedCategory.set(this.selectedCategory() === category ? null : category);
  }

  toggleEditColumn(column: string): void {
    if (this.openColumns.has(column)) {
      this.openColumns.delete(column);
      delete this.newValues[column];
    } else {
      this.openColumns.add(column);
      this.newValues[column] = this.retailArticles().map(() => '');
    }
  }

  isOpen(column: string): boolean {
    return this.openColumns.has(column);
  }

  // Appelé au clic sur "Soumettre"
  onSubmit() {
    this.errors = {};

    // Collecter les lignes modifiées (celles avec une valeur saisie)
    const changedArticles = this.retailArticles().filter(a => {
      const mod = this.modifications[a.id];
      return mod && mod.quantity_change !== null && mod.quantity_change !== 0;
    });

    if (changedArticles.length === 0) {
      return;
    }

    // Valider : pas de stock négatif après modification
    for (const article of changedArticles) {
      const mod = this.modifications[article.id];
      const currentStock = parseInt(article.stock, 10);
      const newStock = currentStock + (mod.quantity_change ?? 0);
      if (newStock < 0) {
        this.errors[article.id] = `Stock insuffisant (actuel: ${currentStock})`;
      }
    }

    if (Object.keys(this.errors).length > 0) {
      return;
    }

    // Séparer les achats des ventes/pertes
    const purchases = changedArticles.filter(a =>
      (this.modifications[a.id].quantity_change ?? 0) > 0
    );

    if (purchases.length > 0) {
      // Il y a des achats → ouvrir la popup pour les prix d'achat
      this.purchaseEntries.set(purchases.map(a => ({
        article_id: a.id,
        name: a.name,
        quantity: this.modifications[a.id].quantity_change!,
        purchase_price: null
      })));
      this.showPurchaseModal.set(true);
    } else {
      // Pas d'achats → envoyer directement
      this.sendChanges();
    }
  }

  // Appelé au clic "OK" de la popup
  onPurchaseModalConfirm() {
    // Valider que tous les prix d'achat sont renseignés
    const entries = this.purchaseEntries();
    const hasEmpty = entries.some(e => e.purchase_price === null || e.purchase_price <= 0);
    if (hasEmpty) {
      return;
    }

    // Injecter les prix d'achat dans les modifications
    for (const entry of entries) {
      // Le purchase_price sera envoyé au backend
    }

    this.showPurchaseModal.set(false);
    this.sendChanges();
  }

  onPurchaseModalCancel() {
    this.showPurchaseModal.set(false);
    this.purchaseEntries.set([]);
  }

  private sendChanges() {
    const entries = this.purchaseEntries();
    const changes: StockChange[] = this.retailArticles()
      .filter(a => {
        const mod = this.modifications[a.id];
        return mod && mod.quantity_change !== null && mod.quantity_change !== 0;
      })
      .map(a => {
        const mod = this.modifications[a.id];
        const purchaseEntry = entries.find(e => e.article_id === a.id);
        return {
          id: a.id,
          quantity_change: mod.quantity_change!,
          is_expired: mod.is_expired,
          purchase_price: purchaseEntry?.purchase_price ?? undefined
        };
      });

    this.clientService.submitChanges(changes).subscribe(response => {
      if (response) {
        // Recharger les articles après modification
        this.loadArticles();
        this.purchaseEntries.set([]);
      }
    });
  }

  onCancel() {
    // Reset toutes les modifications
    this.retailArticles().forEach(a => {
      this.modifications[a.id] = { quantity_change: null, is_expired: false };
    });
    this.errors = {};
    this.openColumns.clear();
    this.newValues = {};
  }
}
