import { Component } from '@angular/core';
import { MobileHeaderComponent } from '../../../layouts/mobile-header/mobile-header.component';
import { BottomNavMobileComponent } from '../../../layouts/bottom-nav-mobile/bottom-nav-mobile.component';

@Component({
  selector: 'app-validate-product-page',
  imports: [MobileHeaderComponent, BottomNavMobileComponent],
  templateUrl: './validate-product-page.component.html',
  styleUrl: './validate-product-page.component.css'
})
export class ValidateProductPageComponent {

}
