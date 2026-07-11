import axiosInstance from "../axiosInstance.ts";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import type {GroceryListResponse} from "../types/responses/GroceryListResponse.ts";
import API_ENDPOINTS from "../../constants/apiEndpoints.ts";
import type {IGroceryCreateItem} from "../types/requests/grocery/CreateGroceryItem.ts";
import type {IGroceryDetail} from "../../types/IGroceryDetail.ts";
import type {IGroceryDetailApiResponse} from "../types/responses/GroceryDetailResponse.ts";
import type {IPayloadGroceryItemUpdate} from "../types/requests/grocery/UpdateGroceryItem.ts";
import type {IGroceryFilterParams} from "../types/requests/grocery/GroceryFilterParams.ts";
import type {IGroceryBulkUpdatePayload} from "../types/requests/grocery/BulkUpdateGroceryItem.ts";


export const getGroceries = async (filters?: IGroceryFilterParams): Promise<IGroceryListItem[]> => {
    const response = await axiosInstance.get<GroceryListResponse[]>(API_ENDPOINTS.GROCERY.GROCERY_LIST, {
        params: filters
    });
    const grocery_list: IGroceryListItem[] = response.data.map(item => ({
        ...item
    }));
    return grocery_list;
}

export const createGroceries = async (newItem: IGroceryCreateItem): Promise<void> => {
    await axiosInstance.post<void>(API_ENDPOINTS.GROCERY.GROCERY_ADD, newItem);
    return;
}

export const getGroceryDetail = async (grocery_id: string): Promise<IGroceryDetail> => {
    const response = await axiosInstance.get<IGroceryDetailApiResponse>(API_ENDPOINTS.GROCERY.GROCERY_DETAIL.replace(':id', grocery_id));
    return response.data;
}

export const updateGrocery = async (grocery_id: string, payload: IPayloadGroceryItemUpdate): Promise<void> => {
    await axiosInstance.put<void>(API_ENDPOINTS.GROCERY.GROCERY_UPDATE.replace(':id', grocery_id), payload);
    return;
}

export const deleteGrocery = async (grocery_id: string): Promise<void> => {
    await axiosInstance.delete<void>(API_ENDPOINTS.GROCERY.GROCERY_DELETE.replace(':id', grocery_id));
    return;
}

export const bulkUpdateShouldInclude = async (payload: IGroceryBulkUpdatePayload): Promise<IGroceryListItem[]> => {
    const response = await axiosInstance.patch<GroceryListResponse[]>(API_ENDPOINTS.GROCERY.GROCERY_BULK_SHOULD_INCLUDE, payload);
    const updated_items: IGroceryListItem[] = response.data.map(item => ({
        ...item
    }));
    return updated_items;
}