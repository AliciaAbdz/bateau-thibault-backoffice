import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { tap } from 'rxjs';

interface AuthResponse {
  refresh: string;
  access: string;
}
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  
  private apiUrl = 'http://localhost:8000/api/auth';


  constructor(private http:HttpClient) { }

  login(username : string, password : string ) {
      return this.http.post<AuthResponse>(`${this.apiUrl}/login/`, { username, password }).pipe(
      tap(response => {
        // Sauvegarder les tokens
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
      })
    );
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}
