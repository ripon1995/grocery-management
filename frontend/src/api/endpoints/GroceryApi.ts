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
import type {IApiResponse} from "../../types/IApiResponse.ts";


const toGroceryListItem = (item: GroceryListResponse): IGroceryListItem => ({...item});

//  --------------- GENERIC for get request ---------------------
async function apiGet<T>(url: string, params?: object): Promise<T> {
    const response = await axiosInstance.get<IApiResponse<T>>(url, {params});
    return response.data.data;
}

// ---------------- GENERICS -------------------------------------
export const getGroceries = async (filters?: IGroceryFilterParams): Promise<IGroceryListItem[]> => {
    const response = await apiGet<GroceryListResponse[]>(API_ENDPOINTS.GROCERY.GROCERY_LIST, filters);
    return response.map(item => (toGroceryListItem(item)));
}

export const getGroceryDetail = async (grocery_id: string): Promise<IGroceryDetail> => {
    return await apiGet<IGroceryDetailApiResponse>(API_ENDPOINTS.GROCERY.GROCERY_DETAIL.replace(':id', grocery_id))
}



export const createGroceries = async (newItem: IGroceryCreateItem): Promise<void> => {
    await axiosInstance.post<void>(API_ENDPOINTS.GROCERY.GROCERY_ADD, newItem);
    return;
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
    const response = await axiosInstance.patch<IApiResponse<GroceryListResponse[]>>(API_ENDPOINTS.GROCERY.GROCERY_BULK_SHOULD_INCLUDE, payload);
    return response.data.data.map(item => (toGroceryListItem(item)));
}