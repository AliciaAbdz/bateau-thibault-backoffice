import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Product, User } from '../../models/models';
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

  private templateProducts: Product[] = [
    { id: 1, name: "Alec", firstname: "Baldwin", email: "alec.baldwin@star.com" },
    { id: 2, name: "Sivan", firstname: "Cozzo", email: "sivan.cozzo@star.com" }
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

  getAllProducts() {
    return this.http.get<Product[]>(`${this.apiUrl}/products`,{ withCredentials: true }).pipe(
      map(products => products.length > 0 ? products : this.templateProducts),
      catchError(error => {
        console.error('Error fetching products:', error);
        return of(this.templateProducts);
      })
    );
  }

  getTeamMembers(id:number) {
    return this.http.get<User[]>(`${this.apiUrl}/users/${id}/team`,{ withCredentials: true }).pipe(
      map(members => members.length > 0 ? members : this.templateTeam),
      catchError(error => {
        console.error('Error fetching team members:', error);
        return of(this.templateTeam);
    })
    );
  }

}
