import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Product, User } from '../../models/models';

@Injectable({
  providedIn: 'root'
})
export class ClientService {

  private apiUrl = 'http://localhost:8000/api/client';

  constructor(private http:HttpClient) { }

  getAllUsers() {
    return this.http.get<User[]>(`${this.apiUrl}/users`);
  }

  getAllProducts() {
    return this.http.get<Product[]>(`${this.apiUrl}/products`);
  }
}
