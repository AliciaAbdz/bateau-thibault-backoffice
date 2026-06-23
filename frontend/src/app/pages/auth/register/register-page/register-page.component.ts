import { Component } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MobileHeaderComponent } from '../../../../layouts/mobile-header/mobile-header.component';
import { BottomNavMobileComponent } from '../../../../layouts/bottom-nav-mobile/bottom-nav-mobile.component';

@Component({
  selector: 'app-register-page',
  imports: [MobileHeaderComponent, BottomNavMobileComponent, FormsModule, RouterLink],
  templateUrl: './register-page.component.html',
  styleUrl: './register-page.component.css'
})
export class RegisterPageComponent {

  username = '';
  password = '';
  confirmPassword = '';
  errorMessage = '';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  onRegister() {
    this.errorMessage = '';

    if (!this.username || !this.password || !this.confirmPassword) {
      this.errorMessage = 'Veuillez remplir tous les champs.';
      return;
    }

    if (this.password !== this.confirmPassword) {
      this.errorMessage = 'Les mots de passe ne correspondent pas.';
      return;
    }

    if (this.password.length < 8) {
      this.errorMessage = 'Le mot de passe doit contenir au moins 8 caractères.';
      return;
    }

    this.http.post<{ access: string; refresh: string }>('http://localhost:8000/api/auth/register/', {
      username: this.username,
      password: this.password
    }).subscribe({
      next: (response) => {
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        if (err.error?.username) {
          this.errorMessage = 'Ce nom d\'utilisateur est déjà pris.';
        } else if (err.error?.password) {
          this.errorMessage = err.error.password[0];
        } else {
          this.errorMessage = 'Erreur lors de l\'inscription.';
        }
      }
    });
  }
}
