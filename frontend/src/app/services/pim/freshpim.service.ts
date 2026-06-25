import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {
  LabelAutofillResponse,
  OmnichannelExportResponse,
  PimAsset,
  PimAttributeValue,
  PimFamily,
  PimProductDetail,
  PimProductListItem,
  PimStatus,
  PimTranslation,
} from '../../models/pim.models';

@Injectable({ providedIn: 'root' })
export class FreshPimService {
  private apiUrl = 'http://localhost:8000/api/pim';

  constructor(private http: HttpClient) {}

  // ----- Référentiel -----
  getFamilies(): Observable<PimFamily[]> {
    return this.http.get<PimFamily[]>(`${this.apiUrl}/families/`);
  }

  getFamily(id: number): Observable<PimFamily> {
    return this.http.get<PimFamily>(`${this.apiUrl}/families/${id}/`);
  }

  // ----- Produits -----
  listProducts(filters?: { status?: PimStatus; family?: number }): Observable<PimProductListItem[]> {
    let params = new HttpParams();
    if (filters?.status) params = params.set('status', filters.status);
    if (filters?.family) params = params.set('family', String(filters.family));
    return this.http.get<PimProductListItem[]>(`${this.apiUrl}/products/`, { params });
  }

  getProduct(id: number): Observable<PimProductDetail> {
    return this.http.get<PimProductDetail>(`${this.apiUrl}/products/${id}/`);
  }

  createProduct(payload: { sku: string; family_id: number }): Observable<PimProductDetail> {
    return this.http.post<PimProductDetail>(`${this.apiUrl}/products/`, payload);
  }

  transition(productId: number, to: PimStatus): Observable<PimProductDetail> {
    return this.http.post<PimProductDetail>(`${this.apiUrl}/products/${productId}/transition/`, { to });
  }

  // ----- Reconnaissance d'étiquette (auto-remplissage IA) -----
  autofillFromLabel(productId: number, file: File): Observable<LabelAutofillResponse> {
    const form = new FormData();
    form.append('image', file);
    return this.http.post<LabelAutofillResponse>(
      `${this.apiUrl}/products/${productId}/autofill-from-label/`, form);
  }

  // ----- Translations -----
  upsertTranslation(productId: number, t: PimTranslation): Observable<PimTranslation> {
    const payload = { ...t, product: productId };
    if (t.id) {
      return this.http.put<PimTranslation>(`${this.apiUrl}/translations/${t.id}/`, payload);
    }
    return this.http.post<PimTranslation>(`${this.apiUrl}/translations/`, payload);
  }

  // ----- Attribute values -----
  upsertAttributeValue(productId: number, v: PimAttributeValue): Observable<PimAttributeValue> {
    const payload = { ...v, product: productId };
    if (v.id) {
      return this.http.put<PimAttributeValue>(`${this.apiUrl}/attribute-values/${v.id}/`, payload);
    }
    return this.http.post<PimAttributeValue>(`${this.apiUrl}/attribute-values/`, payload);
  }

  // ----- Assets -----
  addAsset(productId: number, a: PimAsset): Observable<PimAsset> {
    const payload = { ...a, product: productId };
    return this.http.post<PimAsset>(`${this.apiUrl}/assets/`, payload);
  }

  deleteAsset(assetId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/assets/${assetId}/`);
  }

  // ----- Export omnicanal -----
  export(channel: string, lang: string): Observable<OmnichannelExportResponse> {
    const params = new HttpParams().set('channel', channel).set('lang', lang);
    return this.http.get<OmnichannelExportResponse>(`${this.apiUrl}/export/`, { params });
  }
}
