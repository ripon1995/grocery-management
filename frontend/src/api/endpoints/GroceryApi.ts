import axios from "axios";
import axiosInstance from "../axiosInstance.ts";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import type {GroceryListResponse} from "../types/responses/GroceryListResponse.ts";
import API_ENDPOINT from "../../constants/apiEndpoints.ts";
import type {IGroceryCreateItem} from "../types/requests/CreateGroceryItem.ts";
import type {IGroceryDetail} from "../../types/IGroceryDetail.ts";
import type {IGroceryDetailApiResponse} from "../types/responses/GroceryDetailResponse.ts";
import {BaseError} from "../types/common.ts";
import type {IPayloadGroceryItemUpdate} from "../types/requests/UpdateGroceryItem.ts";


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
    try {
        const response = await axiosInstance.get<IGroceryDetailApiResponse>(API_ENDPOINT.GROCERY_DETAIL.replace(':id', grocery_id));
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response?.data) {
            throw new BaseError(error.response.data);
        }
        // Returns the object with your default fallbacks
        throw new BaseError();
    }
}

export const updateGrocery = async (grocery_id: string, payload: IPayloadGroceryItemUpdate): Promise<void> => {
    try {
        await axiosInstance.put<void>(API_ENDPOINT.GROCERY_UPDATE.replace(':id', grocery_id), payload);
        return;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response?.data) {
            throw new BaseError(error.response.data);
        }
        // Returns the object with your default fallbacks
        throw new BaseError();
    }
}