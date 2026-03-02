import { Routes } from '@angular/router';

export const routes: Routes = [

  {
    path: 'home',
    loadComponent: () => import('./pages/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'details-produits',
    loadComponent: () => import('./pages/details-produits/details-produits.component').then((m) => m.DetailsProduitsComponent )
  }
];
