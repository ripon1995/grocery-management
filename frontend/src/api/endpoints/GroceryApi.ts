import axiosInstance from "../axiosInstance.ts";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import type {GroceryListResponse} from "../types/responses/GroceryListResponse.ts";
import API_ENDPOINT from "../../constants/apiEndpoints.ts";
import type {IGroceryCreateItem} from "../types/requests/CreateGroceryItem.ts";
import type {IGroceryDetail} from "../../types/IGroceryDetail.ts";
import type {IGroceryDetailApiResponse} from "../types/responses/GroceryDetailResponse.ts";


export const getGroceries = async (): Promise<IGroceryListItem[]> => {
    const response = await axiosInstance.get<GroceryListResponse[]>(API_ENDPOINT.GROCERY_LIST);
    const grocery_list: IGroceryListItem[] = response.data.map(item => ({
        ...item
    }));
    console.log(`Fetched ${grocery_list.length} items`);
    return grocery_list;
}

export const createGroceries = async (newItem: IGroceryCreateItem): Promise<void> => {
    await axiosInstance.post<void>(API_ENDPOINT.GROCERY_ADD, newItem);
    return;
}

export const getGroceryDetail = async (grocery_id: string): Promise<IGroceryDetail> => {
    const response = await axiosInstance.get<IGroceryDetailApiResponse>(API_ENDPOINT.GROCERY_DETAIL.replace(':id', grocery_id));
    console.log(response.data)
    return response.data;

}