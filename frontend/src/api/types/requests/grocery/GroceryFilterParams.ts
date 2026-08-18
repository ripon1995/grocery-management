import type {IGroceryDetail} from "../../../../types/IGroceryDetail.ts";


type FilterKeys =
    | 'type'
    | 'current_seller'
    | 'best_seller'
    | 'category'
    | 'should_include'


type IGroceryFilterParams = Partial<Pick<IGroceryDetail, FilterKeys>> & { search?: string };

export type {IGroceryFilterParams}