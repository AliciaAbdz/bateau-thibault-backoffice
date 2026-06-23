import { Component, computed } from '@angular/core';
import { Router } from '@angular/router';
import { TeamCardComponent } from '../../../shared/components/team-card/team-card.component';
import { UserCardComponent } from '../../../shared/components/user-card/user-card.component';
import { ProductsComponent } from '../../../features/dashboard/products/products.component';
import { DataComponent } from '../../../features/dashboard/data/data.component';
import { AddProductPageComponent } from "../../products/add-product-page/add-product-page.component";
import { AppHeaderComponent, UserHeaderData } from '../../../layouts/app-header/app-header.component';
import { BottomNavComponent } from '../../../layouts/bottom-nav/bottom-nav.component';
import { AuthService } from '../../../services/auth/auth.service';

@Component({
  selector: 'app-dashboard-page',
  imports: [TeamCardComponent, UserCardComponent, ProductsComponent, DataComponent, AppHeaderComponent, BottomNavComponent],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.css'
})
export class DashboardPageComponent {
  activeTab: 'products' | 'data' = 'products';

  headerUser = computed<UserHeaderData>(() => {
    const user = this.authService.currentUser();
    return {
      name: (user?.first_name && user?.last_name)
        ? `${user.first_name} ${user.last_name}`
        : user?.username ?? 'Utilisateur',
      role: user?.role ?? 'ROLE_USER'
    };
  });

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onLogout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
