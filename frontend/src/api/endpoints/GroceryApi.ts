import axiosInstance from "../axiosInstance.ts";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import type {ApiGroceryItem} from "../types/responses/GroceryListResponse.ts";
import API_ENDPOINT from "../../constants/apiEndpoints.ts";


const getGroceries = async (): Promise<IGroceryListItem[]> => {
    const response = await axiosInstance.get<ApiGroceryItem[]>(API_ENDPOINT.GROCERY_LIST);
    const grocery_list: IGroceryListItem[] = response.data.map(item => ({
        ...item
    }));
    console.log(`Fetched ${grocery_list.length} items`);
    return grocery_list;
}

export default getGroceries;