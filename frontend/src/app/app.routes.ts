import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'bottom-nav',
    pathMatch: 'full',
  },

  // Layout components urls -> checking
  {
    path: 'app-header',
    loadComponent: () =>
      import('./layouts/app-header/app-header.component').then((m) => m.AppHeaderComponent),
  },
  {
    path: 'bottom-nav',
    loadComponent: () =>
      import('./layouts/bottom-nav/bottom-nav.component').then((m) => m.BottomNavComponent),
  },
  {
    path: 'mobile-header',
    loadComponent: () =>
      import('./layouts/mobile-header/mobile-header.component').then((m) => m.MobileHeaderComponent),
  },

  {
    path: 'dashboard',
    loadComponent: () =>
      import('./pages/dashboard/dashboard-page/dashboard-page.component').then((m) => m.DashboardPageComponent),
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./pages/auth/login/login-page/login-page.component').then((m) => m.LoginPageComponent),
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./pages/auth/register/register-page/register-page.component').then((m) => m.RegisterPageComponent),
  },
  {
    path: 'add-product',
    loadComponent: () =>
      import('./pages/products/add-product-page/add-product-page.component').then((m) => m.AddProductPageComponent),
  },
  {
    path: 'validate-product',
    loadComponent: () =>
      import('./pages/products/validate-product-page/validate-product-page.component').then((m) => m.ValidateProductPageComponent),
  },
]; 