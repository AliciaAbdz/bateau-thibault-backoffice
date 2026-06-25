import { CommonModule } from '@angular/common';
import { Component, OnInit, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin, of, switchMap } from 'rxjs';
import {
  PimAttributeValue,
  PimFamilyAttribute,
  PimProductDetail,
  PimStatus,
  PimTranslation,
} from '../../../models/pim.models';
import { FreshPimService } from '../../../services/pim/freshpim.service';
import { AuthService } from '../../../services/auth/auth.service';

interface AttrFormState {
  fa: PimFamilyAttribute;
  value: string;
  existingId?: number;
  locale: string;
}

interface TransitionTarget {
  label: string;
  to: PimStatus;
  variant: 'primary' | 'success' | 'warning' | 'danger';
}

@Component({
  selector: 'app-pim-detail-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './pim-detail-page.component.html',
  styleUrl: './pim-detail-page.component.css',
})
export class PimDetailPageComponent implements OnInit {
  product = signal<PimProductDetail | null>(null);
  loading = signal(false);
  saving = signal(false);
  error = signal<string | null>(null);
  notice = signal<string | null>(null);

  activeLocale: 'fr' | 'en' = 'fr';
  translations: Record<'fr' | 'en', PimTranslation> = {
    fr: { locale: 'fr', name: '', marketing_description: '' },
    en: { locale: 'en', name: '', marketing_description: '' },
  };
  attrForm: AttrFormState[] = [];

  newAssetUrl = '';
  newAssetAlt = '';

  // Le rôle est dans le JWT décodé par AuthService
  role = computed(() => this.auth.currentUser()?.role ?? '');
  userId = computed(() => this.auth.currentUser()?.user_id ?? null);

  constructor(
    private route: ActivatedRoute,
    private pim: FreshPimService,
    private auth: AuthService,
  ) {}

  ngOnInit(): void {
    this.route.paramMap
      .pipe(switchMap((params) => {
        const id = Number(params.get('id'));
        if (!id) return of(null);
        this.loading.set(true);
        return this.pim.getProduct(id);
      }))
      .subscribe({
        next: (p) => {
          this.loading.set(false);
          if (p) this.hydrate(p);
        },
        error: (err) => {
          this.loading.set(false);
          this.error.set(err?.error?.detail || 'Produit introuvable');
        },
      });
  }

  hydrate(p: PimProductDetail): void {
    this.product.set(p);
    // Reset & remplissage des translations
    this.translations = {
      fr: { locale: 'fr', name: '', marketing_description: '' },
      en: { locale: 'en', name: '', marketing_description: '' },
    };
    p.translations.forEach((t) => {
      if (t.locale === 'fr' || t.locale === 'en') {
        this.translations[t.locale] = { ...t };
      }
    });
    // Construction du formulaire dynamique d'attributs depuis la famille
    this.attrForm = p.family.family_attributes.map((fa) => {
      const locale = fa.attribute.is_localizable ? this.activeLocale : '-';
      const existing = p.attribute_values.find(
        (v) => v.attribute === fa.attribute.id && v.locale === locale,
      );
      return {
        fa,
        locale,
        value: existing?.value ?? '',
        existingId: existing?.id,
      };
    });
  }

  switchLocale(locale: 'fr' | 'en'): void {
    this.activeLocale = locale;
    // Recompute attr values for localizable attrs
    const p = this.product();
    if (!p) return;
    this.attrForm = this.attrForm.map((a) => {
      if (!a.fa.attribute.is_localizable) return a;
      const existing = p.attribute_values.find(
        (v) => v.attribute === a.fa.attribute.id && v.locale === locale,
      );
      return {
        ...a,
        locale,
        value: existing?.value ?? '',
        existingId: existing?.id,
      };
    });
  }

  save(): void {
    const p = this.product();
    if (!p) return;
    this.saving.set(true);
    this.notice.set(null);
    this.error.set(null);

    const ops = [];
    // Translations FR + EN si renseignées
    for (const locale of ['fr', 'en'] as const) {
      const t = this.translations[locale];
      if (t.name.trim()) {
        ops.push(this.pim.upsertTranslation(p.id, t));
      }
    }
    // Attribute values
    for (const a of this.attrForm) {
      if (a.value === '' || a.value === null || a.value === undefined) continue;
      const payload: PimAttributeValue = {
        id: a.existingId,
        attribute: a.fa.attribute.id,
        locale: a.locale,
        value: String(a.value),
      };
      ops.push(this.pim.upsertAttributeValue(p.id, payload));
    }

    forkJoin(ops.length ? ops : [of(null)]).subscribe({
      next: () => {
        this.pim.getProduct(p.id).subscribe((fresh) => {
          this.hydrate(fresh);
          this.saving.set(false);
          this.notice.set('Modifications enregistrées.');
        });
      },
      error: (err) => {
        this.saving.set(false);
        this.error.set(err?.error?.detail || JSON.stringify(err?.error) || 'Erreur de sauvegarde');
      },
    });
  }

  addAsset(): void {
    const p = this.product();
    if (!p || !this.newAssetUrl.trim()) return;
    this.pim.addAsset(p.id, {
      type: 'image',
      url: this.newAssetUrl.trim(),
      position: p.assets.length,
      alt_text: this.newAssetAlt,
    }).subscribe({
      next: () => {
        this.newAssetUrl = '';
        this.newAssetAlt = '';
        this.pim.getProduct(p.id).subscribe((fresh) => this.hydrate(fresh));
      },
      error: (err) => this.error.set(err?.error?.detail || 'Échec ajout asset'),
    });
  }

  removeAsset(id?: number): void {
    if (!id) return;
    this.pim.deleteAsset(id).subscribe({
      next: () => {
        const p = this.product();
        if (p) this.pim.getProduct(p.id).subscribe((fresh) => this.hydrate(fresh));
      },
    });
  }

  // ---------- Workflow ----------

  availableTransitions = computed<TransitionTarget[]>(() => {
    const p = this.product();
    if (!p) return [];
    const role = this.role();
    const isOwner = p.created_by === this.userId();
    const isPimAdmin = role === 'ROLE_PIM_ADMIN';

    const out: TransitionTarget[] = [];
    if (p.status === 'draft') {
      if (isPimAdmin || isOwner) {
        out.push({ label: 'Soumettre pour validation', to: 'in_review', variant: 'primary' });
      }
    } else if (p.status === 'in_review') {
      if (isPimAdmin) {
        out.push({ label: 'Publier ✓', to: 'published', variant: 'success' });
        out.push({ label: 'Rejeter (renvoyer brouillon)', to: 'draft', variant: 'warning' });
      }
    } else if (p.status === 'published') {
      if (isPimAdmin) out.push({ label: 'Archiver', to: 'archived', variant: 'danger' });
    } else if (p.status === 'archived') {
      if (isPimAdmin) out.push({ label: 'Réouvrir en brouillon', to: 'draft', variant: 'primary' });
    }
    return out;
  });

  transition(to: PimStatus): void {
    const p = this.product();
    if (!p) return;
    this.notice.set(null);
    this.error.set(null);
    this.pim.transition(p.id, to).subscribe({
      next: (fresh) => {
        this.hydrate(fresh);
        this.notice.set(`Statut → ${to}`);
      },
      error: (err) => {
        this.error.set(err?.error?.error || err?.error?.detail || 'Transition refusée');
      },
    });
  }

  buttonClass(variant: 'primary' | 'success' | 'warning' | 'danger'): string {
    switch (variant) {
      case 'success': return 'bg-green-600 hover:bg-green-700 text-white';
      case 'warning': return 'bg-yellow-500 hover:bg-yellow-600 text-white';
      case 'danger': return 'bg-red-600 hover:bg-red-700 text-white';
      default: return 'bg-blue-600 hover:bg-blue-700 text-white';
    }
  }
}
