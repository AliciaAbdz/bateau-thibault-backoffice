import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
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
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/dashboard/dashboard-page/dashboard-page.component').then((m) => m.DashboardPageComponent),
  },
  {
    path: 'add-product',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/products/add-product-page/add-product-page.component').then((m) => m.AddProductPageComponent),
  },
  {
    path: 'validate-product',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/products/validate-product-page/validate-product-page.component').then((m) => m.ValidateProductPageComponent),
  },
]; 