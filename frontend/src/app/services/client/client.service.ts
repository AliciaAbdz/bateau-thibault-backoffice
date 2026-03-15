import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { RetailArticle, User } from '../../models/models';
import { catchError, map, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ClientService {

  private apiUrl = 'http://localhost:8000/api/client';

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
    let users = this.http.get<User[]>(`${this.apiUrl}/users`,{ withCredentials: true }).pipe(
      map(users => users.length > 0 ? users : this.templateUsers), // if no users, return templateUsers
      catchError(error => { // if error fetching, return templateUsers
        console.error('Error fetching users:', error); 
        return of(this.templateUsers);
      })
    );
    return users;
  }

  getAllRetailArticles(userId:number) {
    return this.http.get<RetailArticle[]>(`${this.apiUrl}/articles/${userId}`,{ withCredentials: true }).pipe(
      map(articles => articles.length > 0 ? articles : this.templatearticles),
      catchError(error => {
        console.error('Error fetching articles:', error);
        return of(this.templatearticles);
      })
    );
  }

  getTeamMembers(userId:number) {
    return this.http.get<User[]>(`${this.apiUrl}/users/${userId}/team`,{ withCredentials: true }).pipe(
      map(members => members.length > 0 ? members : this.templateTeam),
      catchError(error => {
        console.error('Error fetching team members:', error);
        return of(this.templateTeam);
    })
    );
  }

  updateRetailArticles(userId:number, articles:RetailArticle[]) {
    return this.http.put<RetailArticle[]>(`${this.apiUrl}/articles/${userId}`,articles,{ withCredentials: true }).pipe(
      map(articles => articles.length > 0 ? articles : this.templatearticles),
      catchError(error => {
        console.error('Error updating articles:', error);
        return of(this.templatearticles);
      })
    );
  }

  deleteRetailArticles(userId:number, articles:RetailArticle[]) {
    return this.http.put<RetailArticle[]>(`${this.apiUrl}/articles/archive/${userId}`,articles,{ withCredentials: true }).pipe(
      map(articles => articles.length > 0 ? articles : this.templatearticles),
      catchError(error => {
        console.error('Error archiving articles:', error);
        return of(this.templatearticles);
      })
    );
  }
}