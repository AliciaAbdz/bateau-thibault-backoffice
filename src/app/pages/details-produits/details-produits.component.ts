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

  ngOnInit() {
    console.log("skhnsjldgnsdglsdg,skmw:fs")
    this.getProducts();
  }
  getProducts() {
    this.productsService.getProductsFromJson().subscribe(
      (response: Product[]) => {
        console.log("Product list : ", response)
        return response;
      },
      (error) => {
        alert('Fail loading json data...');
      },
    );
  }
}
