import { Component } from '@angular/core';
import { MobileHeaderComponent } from '../../../layouts/mobile-header/mobile-header.component';
import { BottomNavMobileComponent } from '../../../layouts/bottom-nav-mobile/bottom-nav-mobile.component';

@Component({
  selector: 'app-add-product-page',
  imports: [MobileHeaderComponent, BottomNavMobileComponent],
  templateUrl: './add-product-page.component.html',
  styleUrl: './add-product-page.component.css'
})
export class AddProductPageComponent {

}
