export type PimStatus = 'draft' | 'in_review' | 'published' | 'archived';
export type AttributeType = 'text' | 'number' | 'bool' | 'select';

export interface PimAttribute {
  id: number;
  code: string;
  label: string;
  type: AttributeType;
  options: string[];
  is_localizable: boolean;
}

export interface PimFamilyAttribute {
  id: number;
  attribute: PimAttribute;
  is_required: boolean;
}

export interface PimFamily {
  id: number;
  name: string;
  description: string;
  family_attributes: PimFamilyAttribute[];
}

export interface PimTranslation {
  id?: number;
  locale: string;
  name: string;
  marketing_description: string;
}

export interface PimAttributeValue {
  id?: number;
  attribute: number;
  attribute_code?: string;
  attribute_label?: string;
  attribute_type?: AttributeType;
  locale: string;
  value: string;
}

export interface PimAsset {
  id?: number;
  type: 'image' | 'video' | 'pdf';
  url: string;
  position: number;
  alt_text: string;
}

export interface PimProductListItem {
  id: number;
  sku: string;
  family: number;
  family_name: string;
  status: PimStatus;
  completeness: number;
  name_fr: string | null;
  created_at: string;
  updated_at: string;
  published_at: string | null;
}

export interface PimProductDetail {
  id: number;
  sku: string;
  family: PimFamily;
  status: PimStatus;
  completeness: number;
  created_by: number | null;
  created_by_username: string | null;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  translations: PimTranslation[];
  attribute_values: PimAttributeValue[];
  assets: PimAsset[];
}

export interface PimLabelSuggestion {
  attribute: number;
  code: string;
  label: string;
  type: AttributeType;
  value: string;
}

export interface LabelAutofillResponse {
  product: number;
  family: string;
  suggestions: PimLabelSuggestion[];
  ignored: Array<{ code: string; value?: string; raison: string }>;
}

export interface OmnichannelExportResponse {
  channel: string;
  lang: string;
  count: number;
  items: Array<{
    sku: string;
    name: string;
    family: string;
    main_image: string | null;
  }>;
}
