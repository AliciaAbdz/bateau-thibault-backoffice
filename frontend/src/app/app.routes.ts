import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'bottom-nav',
    pathMatch: 'full',
  },

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
]; 