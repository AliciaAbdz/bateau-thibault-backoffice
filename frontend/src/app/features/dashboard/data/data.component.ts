import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ClientService } from '../../../services/client/client.service';
import { AuthService } from '../../../services/auth/auth.service';
import { PurchaseDetail, SaleDetail } from '../../../models/models';
import { forkJoin } from 'rxjs';
import Chart from 'chart.js/auto';

type Period = 'last_week' | 'last_month' | 'last_quarter' | 'last_year';

@Component({
  selector: 'app-data',
  imports: [FormsModule],
  templateUrl: './data.component.html',
  styleUrl: './data.component.css'
})
export class DataComponent implements OnInit, AfterViewInit, OnDestroy {

  @ViewChild('caChart') caChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('margeChart') margeChartRef!: ElementRef<HTMLCanvasElement>;

  private caChartInstance: Chart | null = null;
  private margeChartInstance: Chart | null = null;

  retailerId = 0;

  // Données brutes
  allPurchases: PurchaseDetail[] = [];
  allSales: SaleDetail[] = [];

  // Filtres
  selectedPeriod: Period = 'last_month';
  periods: { value: Period; label: string }[] = [
    { value: 'last_week', label: 'Semaine' },
    { value: 'last_month', label: 'Mois' },
    { value: 'last_quarter', label: 'Trimestre' },
    { value: 'last_year', label: 'Année' },
  ];

  allCategories: string[] = [];
  selectedCategories: Set<string> = new Set();
  showTypeDropdown = false;

  promoMin: number | null = null;
  promoMax: number | null = null;

  // KPIs
  chiffreAffaires = 0;
  caEvolution = 0;
  marge = 0;
  margeEvolution = 0;
  impot = 0;

  private dataLoaded = false;

  constructor(
    private clientService: ClientService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.retailerId = this.authService.getRetailerId() ?? 0;
    this.loadData();
  }

  ngAfterViewInit() {
    if (this.dataLoaded) {
      this.buildCharts();
    }
  }

  ngOnDestroy() {
    this.caChartInstance?.destroy();
    this.margeChartInstance?.destroy();
  }

  loadData() {
    forkJoin({
      purchases: this.clientService.getPurchases(this.retailerId),
      sales: this.clientService.getSales(this.retailerId)
    }).subscribe(({ purchases, sales }) => {
      this.allPurchases = purchases;
      this.allSales = sales;

      // Extraire les catégories uniques
      const cats = new Set<string>();
      sales.forEach(s => cats.add(s.category));
      purchases.forEach(p => cats.add(p.category));
      this.allCategories = Array.from(cats).sort();
      this.allCategories.forEach(c => this.selectedCategories.add(c));

      this.dataLoaded = true;
      this.recalculate();
    });
  }

  // --- Filtres ---

  toggleCategory(cat: string) {
    if (this.selectedCategories.has(cat)) {
      this.selectedCategories.delete(cat);
    } else {
      this.selectedCategories.add(cat);
    }
    this.recalculate();
  }

  isCategorySelected(cat: string): boolean {
    return this.selectedCategories.has(cat);
  }

  onPeriodChange() {
    this.recalculate();
  }

  onPromoFilterChange() {
    this.recalculate();
  }

  toggleTypeDropdown() {
    this.showTypeDropdown = !this.showTypeDropdown;
  }

  // --- Calculs ---

  private getDateRange(period: Period): { start: Date; end: Date } {
    const end = new Date();
    const start = new Date();
    switch (period) {
      case 'last_week': start.setDate(end.getDate() - 7); break;
      case 'last_month': start.setMonth(end.getMonth() - 1); break;
      case 'last_quarter': start.setMonth(end.getMonth() - 3); break;
      case 'last_year': start.setFullYear(end.getFullYear() - 1); break;
    }
    return { start, end };
  }

  private getPreviousDateRange(period: Period): { start: Date; end: Date } {
    const current = this.getDateRange(period);
    const duration = current.end.getTime() - current.start.getTime();
    return {
      start: new Date(current.start.getTime() - duration),
      end: new Date(current.start.getTime())
    };
  }

  private filterByDateAndCategory<T extends { date: string; category: string }>(
    items: T[], start: Date, end: Date
  ): T[] {
    return items.filter(item => {
      const d = new Date(item.date);
      const inDate = d >= start && d <= end;
      const inCategory = this.selectedCategories.has(item.category);
      return inDate && inCategory;
    });
  }

  private filterSalesByPromo(sales: SaleDetail[]): SaleDetail[] {
    if (this.promoMin === null && this.promoMax === null) return sales;
    return sales.filter(s => {
      const disc = s.discount_at_sale;
      if (this.promoMin !== null && disc < this.promoMin) return false;
      if (this.promoMax !== null && disc > this.promoMax) return false;
      return true;
    });
  }

  private recalculate() {
    const { start, end } = this.getDateRange(this.selectedPeriod);
    const prev = this.getPreviousDateRange(this.selectedPeriod);

    // Ventes = sales avec total > 0 (pas les pertes)
    const currentSales = this.filterSalesByPromo(
      this.filterByDateAndCategory(this.allSales, start, end).filter(s => s.total > 0)
    );
    const previousSales = this.filterSalesByPromo(
      this.filterByDateAndCategory(this.allSales, prev.start, prev.end).filter(s => s.total > 0)
    );

    const currentPurchases = this.filterByDateAndCategory(this.allPurchases, start, end);
    const previousPurchases = this.filterByDateAndCategory(this.allPurchases, prev.start, prev.end);

    // CA
    this.chiffreAffaires = currentSales.reduce((sum, s) => sum + s.total, 0);
    const prevCA = previousSales.reduce((sum, s) => sum + s.total, 0);
    this.caEvolution = prevCA > 0 ? Math.round(((this.chiffreAffaires - prevCA) / prevCA) * 100) : 0;

    // Marge
    const totalAchats = currentPurchases.reduce((sum, p) => sum + p.total, 0);
    const prevTotalAchats = previousPurchases.reduce((sum, p) => sum + p.total, 0);
    this.marge = this.chiffreAffaires - totalAchats;
    const prevMarge = prevCA - prevTotalAchats;
    this.margeEvolution = prevMarge !== 0 ? Math.round(((this.marge - prevMarge) / Math.abs(prevMarge)) * 100) : 0;

    // Impôt
    this.impot = this.marge > 0 ? Math.round(this.marge * 0.30) : 0;

    this.buildCharts();
  }

  // --- Charts ---

  private buildCharts() {
    if (!this.caChartRef || !this.margeChartRef) return;

    const { start, end } = this.getDateRange(this.selectedPeriod);
    const currentSales = this.filterSalesByPromo(
      this.filterByDateAndCategory(this.allSales, start, end).filter(s => s.total > 0)
    );
    const currentPurchases = this.filterByDateAndCategory(this.allPurchases, start, end);

    // Grouper par date
    const caByDate = this.groupByDate(currentSales);
    const purchasesByDate = this.groupByDate(currentPurchases);

    const allDates = Array.from(new Set([...Object.keys(caByDate), ...Object.keys(purchasesByDate)])).sort();
    const labels = allDates.map(d => this.formatDate(d));
    const caData = allDates.map(d => caByDate[d] || 0);

    // Marge par date = ventes - achats
    const margeData = allDates.map(d => (caByDate[d] || 0) - (purchasesByDate[d] || 0));

    // CA Chart
    this.caChartInstance?.destroy();
    this.caChartInstance = new Chart(this.caChartRef.nativeElement, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data: caData,
          borderColor: '#7BC67E',
          backgroundColor: 'rgba(123, 198, 126, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 2
        }]
      },
      options: this.getChartOptions()
    });

    // Marge Chart
    this.margeChartInstance?.destroy();
    this.margeChartInstance = new Chart(this.margeChartRef.nativeElement, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data: margeData,
          borderColor: '#7BC67E',
          backgroundColor: 'rgba(123, 198, 126, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          borderWidth: 2
        }]
      },
      options: this.getChartOptions()
    });
  }

  private getChartOptions(): any {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          display: true,
          grid: { display: false },
          ticks: { display: false }
        },
        y: {
          display: true,
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { display: false }
        }
      }
    };
  }

  private groupByDate(items: { date: string; total: number }[]): Record<string, number> {
    const grouped: Record<string, number> = {};
    items.forEach(item => {
      grouped[item.date] = (grouped[item.date] || 0) + item.total;
    });
    return grouped;
  }

  private formatDate(dateStr: string): string {
    const d = new Date(dateStr);
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
  }

  // --- Helpers template ---

  formatNumber(n: number): string {
    return n.toLocaleString('fr-FR');
  }
}
