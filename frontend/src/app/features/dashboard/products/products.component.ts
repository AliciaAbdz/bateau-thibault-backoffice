import { Component, computed, signal } from '@angular/core';
import { RetailArticleDisplay } from '../../../models/models';
import { ProductsService } from '../../../services/products/products.service';
import { FormsModule } from '@angular/forms';

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
  
  userId = 1; // Change for userId gathered by JWT

  constructor(private productService:ProductsService){}
  ngOnInit() {
    this.productService.getArticles(this.userId).subscribe(data => {
      this.retailArticles.set(data);
      const cats = this.categories();
      if (cats.length > 0) this.selectedCategory.set(cats[0]);
    });
  }

  selectCategory(category: string) {
    this.selectedCategory.set(this.selectedCategory() === category ? null : category);
  }


  // Colonnes éditables ouvertes (plusieurs possibles)
  openColumns: Set<string> = new Set();

  // Nouvelles valeurs saisies par l'utilisateur
  newValues: Record<string, string[]> = {};

  toggleEditColumn(column: string): void {
    if (this.openColumns.has(column)) {
      // save data before delete
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
}
