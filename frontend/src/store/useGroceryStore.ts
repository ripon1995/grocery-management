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
        set({isLoading: true, error: null});
        try {
            const data = await getGroceries();
            set({groceries: data, isLoading: false});
        } catch (err) {
            console.log(err);
            set({isLoading: false});
        }
    }
}));

export default useGroceryStore;