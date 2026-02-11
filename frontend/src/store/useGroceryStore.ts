import {create} from "zustand";
import type {IGroceryListItem} from "../types/IGroceryList.ts";
import {getGroceries, createGroceries} from "../api/endpoints/GroceryApi.ts";
import type {IGroceryCreateItem} from "../api/types/requests/CreateGroceryItem.ts";


interface IGroceryState {
    groceries: IGroceryListItem[];
    isLoading: boolean;
    error: string | null;

    // actions
    fetchGroceries: () => Promise<void>;
    addGroceries: (newItem: IGroceryCreateItem) => Promise<void>;
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
    },
    addGroceries: async (newItem: IGroceryCreateItem) => {
        try {
            await createGroceries(newItem);
            set({isLoading: false});
        } catch (err) {
            console.log(err);
            set({isLoading: false});
        }
    }
}));

export default useGroceryStore;