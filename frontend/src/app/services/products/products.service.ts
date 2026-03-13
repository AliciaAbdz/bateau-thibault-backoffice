import { Injectable } from '@angular/core';
import { Product } from '../../models/models';
import { ClientService } from '../client/client.service';

@Injectable({
  providedIn: 'root'
})
export class ProductsService {

  constructor(private client:ClientService) { }

  addProducts(products:Product[]) {
  }

  modifyProducts(products:Product[]) {
  }

  deleteProducts(products:Product[]) {
  }
}
