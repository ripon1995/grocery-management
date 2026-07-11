import type {GroceryType, Seller, GroceryCategory} from "../../../../constants/enums.ts";


export interface IGroceryFilterParams {
    type?: GroceryType;
    current_seller?: Seller;
    best_seller?: Seller;
    category?: GroceryCategory;
    should_include?: boolean;
    search?: string;
}
