import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { OmnichannelExportResponse } from '../../../models/pim.models';
import { FreshPimService } from '../../../services/pim/freshpim.service';

@Component({
  selector: 'app-pim-export-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './pim-export-page.component.html',
  styleUrl: './pim-export-page.component.css',
})
export class PimExportPageComponent {
  channel = 'pos';
  lang = 'fr';

  result = signal<OmnichannelExportResponse | null>(null);
  errorPayload = signal<any>(null);
  loading = signal(false);

  channels = [
    { value: 'pos', label: 'POS (FreshPilot, back-office vente)', implemented: true },
    { value: 'ecommerce', label: 'E-commerce (decathlon.fr-like)', implemented: false },
    { value: 'mobile', label: 'Application mobile (payload allégé)', implemented: false },
    { value: 'marketplace', label: 'Marketplace (CSV-friendly, Amazon-like)', implemented: false },
  ];
  langs = [
    { value: 'fr', label: '🇫🇷 Français' },
    { value: 'en', label: '🇬🇧 English' },
  ];

  constructor(private pim: FreshPimService) {}

  run(): void {
    this.loading.set(true);
    this.result.set(null);
    this.errorPayload.set(null);
    this.pim.export(this.channel, this.lang).subscribe({
      next: (data) => {
        this.result.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.errorPayload.set(err?.error || { error: 'Erreur réseau' });
        this.loading.set(false);
      },
    });
  }

  payloadJson(): string {
    return JSON.stringify(this.result() ?? this.errorPayload(), null, 2);
  }
}
