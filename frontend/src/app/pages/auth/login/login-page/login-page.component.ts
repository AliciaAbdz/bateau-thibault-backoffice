import { Component } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MobileHeaderComponent } from '../../../../layouts/mobile-header/mobile-header.component';
import { BottomNavMobileComponent } from '../../../../layouts/bottom-nav-mobile/bottom-nav-mobile.component';
import { AuthService } from '../../../../services/auth/auth.service';

@Component({
  selector: 'app-login-page',
  imports: [MobileHeaderComponent, BottomNavMobileComponent, FormsModule, RouterLink],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent {

  username = '';
  password = '';
  errorMessage = '';
  private returnUrl = '/dashboard';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
  }

  onLogin() {
    this.errorMessage = '';
    if (!this.username || !this.password) {
      this.errorMessage = 'Veuillez remplir tous les champs.';
      return;
    }

    this.authService.login(this.username, this.password).subscribe({
      next: () => {
        this.router.navigateByUrl(this.returnUrl);
      },
      error: () => {
        this.errorMessage = 'Identifiant ou mot de passe incorrect.';
      }
    });
  }
}
