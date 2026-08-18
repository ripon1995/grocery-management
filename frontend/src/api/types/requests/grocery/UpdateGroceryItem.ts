import type {IGroceryDetail} from "../../../../types/IGroceryDetail.ts";


type ServerGeneratedKeys =
    | 'best_price'
    | 'best_seller'
    | 'stock_status'
    | 'created_at'
    | 'updated_at'

type IPayloadGroceryItemUpdate = Omit<IGroceryDetail, ServerGeneratedKeys>

export type {IPayloadGroceryItemUpdate};