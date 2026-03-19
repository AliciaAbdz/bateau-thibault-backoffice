import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { tap } from 'rxjs';
import { jwtDecode } from 'jwt-decode';

interface AuthResponse {
  refresh: string;
  access: string;
}

interface JwtPayload {
  user_id: number;
  username: string;
  retailer: number | null;
  role: string;
  last_connexion: string | null;
  exp: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'http://localhost:8000/api/auth';
  currentUser = signal<JwtPayload | null>(null);

  constructor(private http: HttpClient) {
    this.loadUserFromToken();
  }

  login(username: string, password: string) {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login/`, { username, password }).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
        this.loadUserFromToken();
      })
    );
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUser.set(null);
  }

  getRetailerId(): number | null {
    return this.currentUser()?.retailer ?? null;
  }

  isAuthenticated(): boolean {
    const user = this.currentUser();
    if (!user) return false;
    return user.exp * 1000 > Date.now();
  }

  private loadUserFromToken() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.currentUser.set(null);
      return;
    }
    try {
      const decoded = jwtDecode<JwtPayload>(token);
      this.currentUser.set(decoded);
    } catch {
      this.currentUser.set(null);
    }
  }
}
