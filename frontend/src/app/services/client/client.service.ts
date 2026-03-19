import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { RetailArticle, StockChange, SubmitChangesResponse, User } from '../../models/models';
import { catchError, map, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ClientService {

  private apiUrl = 'http://localhost:8000/api';

  private templateUsers: User[] = [
    { id: 1, name: "Alec", firstname: "Baldwin", email: "alec.baldwin@star.com" },
    { id: 2, name: "Sivan", firstname: "Cozzo", email: "sivan.cozzo@star.com" }
  ];

  private templatearticles: RetailArticle[] = [
    { id: 1, name: 'Homard', category : 'Crustacé', price: 45, discount_percent: 5, stock: 5, sales: 25, comment: 'blabla' },
    { id: 2, name: 'Araignées', category : 'Crustacé', price: 25, discount_percent: 15, stock: 5, sales: 80, comment: 'blabla' },
    { id: 3, name: 'Bar', category : 'Poisson', price: 20, discount_percent: 5, stock: 5, sales: 25, comment: 'blabla' },
    { id: 4, name: 'Colin', category : 'Poisson', price: 15, discount_percent: 0, stock: 5, sales: 80, comment: 'blabla' },
  ];

  private templateTeam: User[] = [
    { id: 3, name: "Fresh", firstname: "Pilot", email: "fresh.pilot@star.com" },
    { id: 2, name: "Sivan", firstname: "Cozzo", email: "sivan.cozzo@star.com" },
    { id: 1, name: "Alec", firstname: "Baldwin", email: "alec.baldwin@star.com" }

  ];

  constructor(private http:HttpClient) { }

  getAllUsers() {
    return this.http.get<User[]>(`${this.apiUrl}/utilisateurs/`).pipe(
      map(users => users.length > 0 ? users : this.templateUsers),
      catchError(error => {
        console.error('Error fetching users:', error);
        return of(this.templateUsers);
      })
    );
  }

  getAllRetailArticles(retailerId:number) {
    return this.http.get<RetailArticle[]>(`${this.apiUrl}/retailer-articles/?retail=${retailerId}`).pipe(
      map(articles => articles.length > 0 ? articles : this.templatearticles),
      catchError(error => {
        console.error('Error fetching articles:', error);
        return of(this.templatearticles);
      })
    );
  }

  getTeamMembers(userId:number) {
    return this.http.get<User[]>(`${this.apiUrl}/utilisateurs/`).pipe(
      map(members => members.length > 0 ? members : this.templateTeam),
      catchError(error => {
        console.error('Error fetching team members:', error);
        return of(this.templateTeam);
      })
    );
  }

  updateRetailArticle(articleId:number, data: Partial<RetailArticle>) {
    return this.http.patch<RetailArticle>(`${this.apiUrl}/retailer-articles/${articleId}/`, data).pipe(
      catchError(error => {
        console.error('Error updating article:', error);
        return of(null);
      })
    );
  }

  createPurchase(data: {total: number, quantity: number, retailer_article: number}) {
    return this.http.post(`${this.apiUrl}/purchases/`, data).pipe(
      catchError(error => {
        console.error('Error creating purchase:', error);
        return of(null);
      })
    );
  }

  createSale(data: {total: number, quantity: number, retailer_article: number}) {
    return this.http.post(`${this.apiUrl}/sales/`, data).pipe(
      catchError(error => {
        console.error('Error creating sale:', error);
        return of(null);
      })
    );
  }

  submitChanges(changes: StockChange[]) {
    return this.http.post<SubmitChangesResponse>(
      `${this.apiUrl}/retailer-articles/submit-changes/`, changes
    ).pipe(
      catchError(error => {
        console.error('Error submitting changes:', error);
        return of(null);
      })
    );
  }
}