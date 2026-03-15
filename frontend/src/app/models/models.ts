export interface User {
    id : number;
    name : string; 
    firstname : string;
    email : string;
}

export interface Retailer {
    id : number;
    adresse : string; 
}

export interface RetailArticle { 
    id : number;
    name : string;
    category: string;
    price : number;
    discount_percent : number;
    stock: number;
    sales: number;
    comment : string;
}

export interface RetailArticleDisplay {
    id : number;
    name : string;
    category: string;
    price : string;
    discount_price : string;
    discount_percent : string;
    stock: string;
    sales: string;
    comment : string;
}
export interface Purchase {
    id : number;
    date : Date;
    total: number;
    quantity : number;
}

export interface Sale {
    id : number;
    date : Date;
    total: number;
    quantity : number;
}