import { Injectable } from '@angular/core';
import { RetailArticle, RetailArticleDisplay } from '../../models/models';
import { ClientService } from '../client/client.service';
import { map, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProductsService {

  constructor(private client:ClientService) { }

  getArticles(id:number) : Observable<RetailArticleDisplay[]> {
    return this.client.getAllRetailArticles(id).pipe(
      map(articles => articles.map(article => this.toDisplay(article)))
    );
  }

  getRetailerCategory(articles : RetailArticleDisplay[]) : string[]{
    return [...new Set(articles.map(article => article.category))];
  }

  private toDisplay(article: RetailArticle): RetailArticleDisplay {
    const discountPrice = article.price * (1 - article.discount_percent / 100);
    return {
      id: article.id,
      name: article.name,
      category: article.category,
      price: article.price + ' €',
      discount_price: discountPrice.toFixed(2) + ' €',
      discount_percent: article.discount_percent + ' %',
      stock: String(article.stock),
      sales: String(article.sales),
      comment: article.comment,
    };
  }
  addProducts(products:RetailArticle[]) {
  }

  modifyProducts(products:RetailArticle[]) {
  }

  deleteProducts(products:RetailArticle[]) {
  }
}
