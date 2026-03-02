import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Product } from './interface-product';
@Injectable({
  providedIn: 'root',
})
export class ProductService {
  constructor(
    private http: HttpClient,
    private router: Router,
  ) {}

  getProductsFromJson() {
    return this.http.get<Product[]>('/assets/data/products.json');
  }
}
