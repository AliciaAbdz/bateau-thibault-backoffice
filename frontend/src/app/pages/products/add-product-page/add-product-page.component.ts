import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Observable, switchMap, of } from 'rxjs';
import { MobileHeaderComponent } from '../../../layouts/mobile-header/mobile-header.component';
import { BottomNavMobileComponent } from '../../../layouts/bottom-nav-mobile/bottom-nav-mobile.component';
import { ClientService } from '../../../services/client/client.service';

@Component({
  selector: 'app-add-product-page',
  imports: [MobileHeaderComponent, BottomNavMobileComponent, FormsModule],
  templateUrl: './add-product-page.component.html',
  styleUrl: './add-product-page.component.css'
})
export class AddProductPageComponent implements OnInit {

  // Infos du QR code (query params)
  articleId = 0;
  name = '';
  category = '';
  price = 0;
  quantity = 0;
  purchasePrice = 0;

  // Promo définie par l'utilisateur
  promoEnabled = false;
  promoPercent: number | null = null;

  errorMessage = '';
  loading = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private clientService: ClientService
  ) {}

  ngOnInit() {
    const params = this.route.snapshot.queryParams;
    this.articleId = Number(params['id']) || 0;
    this.name = params['name'] || '';
    this.category = params['category'] || '';
    this.price = Number(params['price']) || 0;
    this.quantity = Number(params['quantity']) || 0;
    this.purchasePrice = Number(params['purchase_price']) || 0;
  }

  get discountPrice(): string {
    if (this.promoEnabled && this.promoPercent && this.promoPercent > 0) {
      return (this.price * (1 - this.promoPercent / 100)).toFixed(2);
    }
    return '';
  }

  onValidate() {
    this.errorMessage = '';

    if (!this.articleId) {
      this.errorMessage = 'QR code invalide : ID article manquant.';
      return;
    }

    this.loading = true;

    const hasStock = this.quantity > 0 && this.purchasePrice > 0;
    const discount = this.promoEnabled ? (this.promoPercent ?? 0) : 0;

    // 1) D'abord soumettre le stock (si besoin)
    const stockStep$: Observable<any> = hasStock
      ? this.clientService.submitChanges([{
          id: this.articleId,
          quantity_change: this.quantity,
          is_expired: false,
          purchase_price: this.purchasePrice
        }])
      : of(true);

    // 2) Puis PATCH la promo (séquentiel pour éviter la race condition)
    stockStep$.pipe(
      switchMap(stockResult => {
        if (hasStock && !stockResult) {
          this.errorMessage = 'Erreur lors de l\'ajout au stock.';
          this.loading = false;
          return of(null);
        }
        return this.clientService.updateRetailArticle(this.articleId, {
          unit_price: this.price,
          discount: discount
        } as any);
      })
    ).subscribe((result: any) => {
      this.loading = false;
      if (result === null) return;

      this.router.navigate(['/validate-product'], {
        queryParams: {
          name: this.name,
          category: this.category,
          quantity: this.quantity,
          purchase_price: this.purchasePrice
        }
      });
    });
  }
}
