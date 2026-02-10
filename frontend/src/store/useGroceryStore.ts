import {create} from "zustand";
import type {IGroceryListItem} from "../types/IGroceryList.ts";
import getGroceries from "../api/endpoints/GroceryApi.ts";


interface IGroceryState {
    groceries: IGroceryListItem[];
    isLoading: boolean;
    error: string | null;

    // actions
    fetchGroceries: () => Promise<void>;
}


const useGroceryStore = create<IGroceryState>((set) => ({
    groceries: [],
    isLoading: false,
    error: null,
    fetchGroceries: async () => {
        try {
            const data = await getGroceries();
            set({groceries: data});
        } catch (err) {
            console.log(err);
        }
    }
}));

export default useGroceryStore;