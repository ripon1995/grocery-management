import type {GroceryType, Seller} from "../../../constants/enums.ts";


export interface IGroceryCreateItem {
    name: string;
    brand: string;
    type: GroceryType;
    current_price: number;
    current_seller: Seller;
    low_stock_threshold: number;
    quantity_in_stock: number;
}