import axiosInstance from "../axiosInstance.ts";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import type {ApiGroceryItem} from "../types/responses/GroceryListResponse.ts";


const getGroceries = async (): Promise<IGroceryListItem[]> => {
    const response = await axiosInstance.get<ApiGroceryItem[]>('/api/groceries/');
    const grocery_list: IGroceryListItem[] = response.data.map(item => ({
        ...item
    }));
    console.log(`Fetched ${grocery_list.length} items`);
    return grocery_list;
}

export default getGroceries;