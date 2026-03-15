import { Component } from '@angular/core';
import { MobileHeaderComponent } from '../../../../layouts/mobile-header/mobile-header.component';
import { BottomNavMobileComponent } from '../../../../layouts/bottom-nav-mobile/bottom-nav-mobile.component';

@Component({
  selector: 'app-register-page',
  imports: [MobileHeaderComponent, BottomNavMobileComponent],
  templateUrl: './register-page.component.html',
  styleUrl: './register-page.component.css'
})
export class RegisterPageComponent {

}
