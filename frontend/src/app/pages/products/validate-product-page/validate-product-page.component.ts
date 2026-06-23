import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MobileHeaderComponent } from '../../../layouts/mobile-header/mobile-header.component';
import { BottomNavMobileComponent } from '../../../layouts/bottom-nav-mobile/bottom-nav-mobile.component';

@Component({
  selector: 'app-validate-product-page',
  imports: [MobileHeaderComponent, BottomNavMobileComponent],
  templateUrl: './validate-product-page.component.html',
  styleUrl: './validate-product-page.component.css'
})
export class ValidateProductPageComponent implements OnInit {

  name = '';
  category = '';
  quantity = 0;
  purchasePrice = 0;

  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit() {
    const params = this.route.snapshot.queryParams;
    this.name = params['name'] || '';
    this.category = params['category'] || '';
    this.quantity = Number(params['quantity']) || 0;
    this.purchasePrice = Number(params['purchase_price']) || 0;
  }

  goToDashboard() {
    this.router.navigate(['/dashboard']);
  }
}
