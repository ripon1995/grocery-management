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

export type ExploreJobStatus = 'pending' | 'running' | 'done' | 'failed';

// The 202 from POST /market/explore. job_id is null when none of the groceries were found
export interface IMarketExploreJob {
    job_id: string | null;
    status: ExploreJobStatus;
    not_found_ids: string[];
}

// GET /market/explore/jobs/{job_id}: results fill in as the worker finishes each grocery
export interface IMarketExploreJobStatus {
    job_id: string;
    status: ExploreJobStatus;
    total: number;
    results: IGroceryExploreResult[];
    error: IMarketExploreError | null;
}

export interface IMarketExploreProgress {
    done: number;
    total: number;
}
