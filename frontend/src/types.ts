// Types definition
export interface User {
    id: number;
    name: string;
    email: string;
    registered_at: string;
}

export interface Product {
    id: number;
    name: string;
    price: number;
    category_id: number;
    active: boolean;
}

export interface Order {
    id: number;
    user_id: number;
    order_date: string;
    status: string;
    paid: boolean;
}
