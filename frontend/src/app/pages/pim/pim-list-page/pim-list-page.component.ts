import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { PimFamily, PimProductListItem, PimStatus } from '../../../models/pim.models';
import { FreshPimService } from '../../../services/pim/freshpim.service';
import { AuthService } from '../../../services/auth/auth.service';

@Component({
  selector: 'app-pim-list-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './pim-list-page.component.html',
  styleUrl: './pim-list-page.component.css',
})
export class PimListPageComponent implements OnInit {
  products = signal<PimProductListItem[]>([]);
  families = signal<PimFamily[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);

  statusFilter: PimStatus | '' = '';
  familyFilter: number | '' = '';

  canCreate = computed(() => {
    const role = this.auth.currentUser()?.role;
    return role === 'ROLE_MANUFACTURER' || role === 'ROLE_PIM_ADMIN';
  });

  showCreateModal = signal(false);
  creating = signal(false);
  newSku = '';
  newFamilyId: number | '' = '';
  createError = signal<string | null>(null);

  readonly statuses: { value: PimStatus; label: string; classes: string }[] = [
    { value: 'draft', label: 'Brouillon', classes: 'bg-gray-200 text-gray-700' },
    { value: 'in_review', label: 'En validation', classes: 'bg-yellow-100 text-yellow-800' },
    { value: 'published', label: 'Publié', classes: 'bg-green-100 text-green-800' },
    { value: 'archived', label: 'Archivé', classes: 'bg-red-100 text-red-800' },
  ];

  constructor(private pim: FreshPimService, private auth: AuthService, private router: Router) {}

  openCreate(): void {
    this.newSku = '';
    this.newFamilyId = this.families()[0]?.id ?? '';
    this.createError.set(null);
    this.showCreateModal.set(true);
  }

  closeCreate(): void {
    this.showCreateModal.set(false);
  }

  submitCreate(): void {
    if (!this.newSku.trim() || !this.newFamilyId) {
      this.createError.set('SKU et famille obligatoires');
      return;
    }
    this.creating.set(true);
    this.createError.set(null);
    this.pim.createProduct({ sku: this.newSku.trim(), family_id: Number(this.newFamilyId) }).subscribe({
      next: (created) => {
        this.creating.set(false);
        this.showCreateModal.set(false);
        this.router.navigate(['/pim/products', created.id]);
      },
      error: (err) => {
        this.creating.set(false);
        const payload = err?.error;
        this.createError.set(
          payload?.sku?.[0] || payload?.detail || JSON.stringify(payload) || 'Échec de la création',
        );
      },
    });
  }

  ngOnInit(): void {
    this.pim.getFamilies().subscribe({ next: (f) => this.families.set(f) });
    this.reload();
  }

  reload(): void {
    this.loading.set(true);
    this.error.set(null);
    this.pim
      .listProducts({
        status: this.statusFilter || undefined,
        family: this.familyFilter || undefined,
      })
      .subscribe({
        next: (data) => {
          this.products.set(data);
          this.loading.set(false);
        },
        error: (err) => {
          this.error.set(err?.error?.detail || 'Erreur de chargement');
          this.loading.set(false);
        },
      });
  }

  statusClass(s: PimStatus): string {
    return this.statuses.find((st) => st.value === s)?.classes ?? '';
  }

  statusLabel(s: PimStatus): string {
    return this.statuses.find((st) => st.value === s)?.label ?? s;
  }

  completenessColor(c: number): string {
    if (c >= 80) return 'bg-green-500';
    if (c >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  }
}
