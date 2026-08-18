import type {IGroceryDetail} from "../../../../types/IGroceryDetail.ts";


type ServerGeneratedKeys =
    | 'id'
    | 'best_price'
    | 'best_seller'
    | 'stock_status'
    | 'created_at'
    | 'updated_at'
    | 'should_include'


export type IGroceryCreateItem = Omit<IGroceryDetail, ServerGeneratedKeys>