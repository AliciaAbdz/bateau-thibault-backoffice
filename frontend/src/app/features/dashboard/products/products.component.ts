import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface Product {
  nom: string;
  prix: string;
  prixPromo: string;
  pourcentagePromo: string;
  quantiteStock: string;
  nbArticlesVendus: string;
  commentaire: string;
}

@Component({
  selector: 'app-products',
  host: { class: 'flex flex-col flex-1' },
  imports: [FormsModule],
  templateUrl: './products.component.html',
  styleUrl: './products.component.css'
})
export class ProductsComponent {
  products: Product[] = [
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '5', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '25', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '7', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: 'blabla', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
  ];

  // Colonnes éditables ouvertes (plusieurs possibles)
  openColumns: Set<string> = new Set();

  // Nouvelles valeurs saisies par l'utilisateur
  newValues: Record<string, string[]> = {};

  toggleEditColumn(column: string): void {
    if (this.openColumns.has(column)) {
      this.openColumns.delete(column);
      delete this.newValues[column];
    } else {
      this.openColumns.add(column);
      this.newValues[column] = this.products.map(() => '');
    }
  }

  isOpen(column: string): boolean {
    return this.openColumns.has(column);
  }
}
