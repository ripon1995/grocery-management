import type {GroceryStockStatus, GroceryType, Seller} from "../../../constants/enums.ts";

export interface GroceryListResponse {
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