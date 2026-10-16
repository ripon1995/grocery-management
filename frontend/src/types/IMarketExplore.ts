import type {Seller} from "../constants/enums.ts";

export interface IShopOffer {
    seller: Seller;
    product_name: string;
    price: number;
    url: string | null;
}

export interface IGroceryExploreResult {
    grocery_id: string;
    offers: IShopOffer[];
    cheapest: IShopOffer | null;
}

export interface IMarketExploreResult {
    results: IGroceryExploreResult[];
    not_found_ids: string[];
}

export interface IMarketExploreError {
    message: string;
    detail: string;
}
