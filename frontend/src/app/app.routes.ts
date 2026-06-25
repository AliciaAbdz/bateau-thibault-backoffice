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

  // ----- FreshPIM -----
  {
    path: 'pim',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/pim/pim-list-page/pim-list-page.component').then((m) => m.PimListPageComponent),
  },
  {
    path: 'pim/export',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/pim/pim-export-page/pim-export-page.component').then((m) => m.PimExportPageComponent),
  },
  {
    path: 'pim/products/:id',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/pim/pim-detail-page/pim-detail-page.component').then((m) => m.PimDetailPageComponent),
  },
];