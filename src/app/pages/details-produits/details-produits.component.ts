import { Component } from '@angular/core';
import { Product } from '../../services/products/interface-product';
import { ProductService } from '../../services/products/products';

@Component({
  selector: 'app-details-produits',
  imports: [],
  templateUrl: './details-produits.component.html',
  styleUrl: './details-produits.component.css',
})
export class DetailsProduitsComponent {
  public detailsProduits: Product[] = [];

  constructor(public productsService: ProductService) {}

  getProducts() {
    this.productsService.getProductsFromJson().subscribe(
      (response: Product[]) => {
        return response;
      },
      (error) => {
        alert('Fail loading json data...');
      },
    );
  }
}
