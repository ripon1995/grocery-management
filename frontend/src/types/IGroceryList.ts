import type {Seller, GroceryStockStatus, GroceryType} from "../constants/enums.ts";

export interface IGroceryListItem {
    id: string;
    name: string;
    brand: string;
    type: GroceryType;
    current_price: number;
    current_seller: string;
    low_stock_threshold: number;
    quantity_in_stock: number;
    should_include: boolean;
    best_price: number;
    best_seller: Seller;
    stock_status: GroceryStockStatus;
}