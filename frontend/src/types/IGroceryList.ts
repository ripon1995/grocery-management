import type {BestSeller, GroceryStockStatus, GroceryType} from "../utils/enums.ts";

export interface IGroceryListItem {
    id: string;
    name: string;
    brand: string;
    type: GroceryType;
    current_price: number;
    quantity_required: number;
    low_stock_threshold: number;
    quantity_in_stock: number;
    best_price: number;
    best_seller: BestSeller;
    stock_status: GroceryStockStatus;
    created_at: string; // ISO Date strings are best kept as strings in TS
    updated_at: string;
}