import { Component } from '@angular/core';

@Component({
  selector: 'app-products',
  imports: [],
  templateUrl: './products.component.html',
  styleUrl: './products.component.css'
})
export class ProductsComponent {
  products = [
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '5', edit: '', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '25', edit: '31', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '', edit: '', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '', edit: '', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '7', edit: '', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: '', edit: '5', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
    { nom: 'Hommard', prix: '45€', prixPromo: 'blabla', pourcentagePromo: 'blabla', edit: '', quantiteStock: 'blabla', nbArticlesVendus: 'blabla', commentaire: 'blabla' },
  ];
}
