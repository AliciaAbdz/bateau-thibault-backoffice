import { Component } from '@angular/core';
import { TeamCardComponent } from '../../../shared/components/team-card/team-card.component';
import { UserCardComponent } from '../../../shared/components/user-card/user-card.component';
import { ProductsComponent } from '../../../features/dashboard/products/products.component';
import { DataComponent } from '../../../features/dashboard/data/data.component';
import { AddProductPageComponent } from "../../products/add-product-page/add-product-page.component";
import { AppHeaderComponent } from '../../../layouts/app-header/app-header.component';

@Component({
  selector: 'app-dashboard-page',
  imports: [TeamCardComponent, UserCardComponent, ProductsComponent, DataComponent, UserCardComponent,AppHeaderComponent],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.css'
})
export class DashboardPageComponent {
  activeTab: 'products' | 'data' = 'products';
}
