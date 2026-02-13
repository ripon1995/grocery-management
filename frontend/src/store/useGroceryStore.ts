import {create} from "zustand";
import type {IGroceryListItem} from "../types/IGroceryList.ts";
import {getGroceries, createGroceries, getGroceryDetail, updateGrocery} from "../api/endpoints/GroceryApi.ts";
import type {IGroceryCreateItem} from "../api/types/requests/CreateGroceryItem.ts";
import type {IGroceryDetail} from "../types/IGroceryDetail.ts";
import type {IPayloadGroceryItemUpdate} from "../api/types/requests/UpdateGroceryItem.ts";


interface IGroceryState {
    groceries: IGroceryListItem[];
    grocery: IGroceryDetail | null;
    isLoading: boolean;
    error: string | null;

    // actions
    fetchGroceries: () => Promise<void>;
    addGroceries: (newItem: IGroceryCreateItem) => Promise<void>;
    getGroceryDetail: (grocery_id: string) => Promise<void>;
    updateGroceryDetail: (grocery_id: string, payload: IPayloadGroceryItemUpdate) => Promise<void>;
}


const useGroceryStore = create<IGroceryState>((set) => ({
    groceries: [],
    isLoading: false,
    grocery: null,
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
    },
    getGroceryDetail: async (grocery_id: string) => {
        set({grocery: null, isLoading: true});
        try {
            const data = await getGroceryDetail(grocery_id);
            set({grocery: data, isLoading: false});
        } catch (err: any) {
            console.log(err);
            set({error: err.message, isLoading: false});
        }
    },
    updateGroceryDetail: async (grocery_id: string, payload: IPayloadGroceryItemUpdate) => {
        set({isLoading: true})
        try {
            await updateGrocery(grocery_id, payload);
            set({isLoading: false});
        } catch (err: any) {
            console.log(err);
            set({error: err.message, isLoading: false});
        }
    }
}));

export default useGroceryStore;