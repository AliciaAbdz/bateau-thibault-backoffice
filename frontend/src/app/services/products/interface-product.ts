export interface Product {
  id: string;
  name: string;
  category: number;
  owner: string;
  unit: string;
  comments: string;
  availability: boolean;
  price: number;
  price_on_sale: number;
  discount: number;
  sale: boolean;
  quantity_stock: number;
  quantity_sold: number;
}
