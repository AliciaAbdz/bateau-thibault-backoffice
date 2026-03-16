import { Component } from '@angular/core';
import { MobileHeaderComponent } from '../../../../layouts/mobile-header/mobile-header.component';
import { BottomNavMobileComponent } from '../../../../layouts/bottom-nav-mobile/bottom-nav-mobile.component';

@Component({
  selector: 'app-login-page',
  imports: [MobileHeaderComponent, BottomNavMobileComponent],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent {

}
