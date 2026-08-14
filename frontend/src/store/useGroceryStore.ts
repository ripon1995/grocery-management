import {create} from "zustand";
import type {IGroceryListItem} from "../types/IGroceryList.ts";
import {
    getGroceries,
    createGroceries,
    getGroceryDetail,
    updateGrocery,
    deleteGrocery,
    bulkUpdateShouldInclude
} from "../api/endpoints/GroceryApi.ts";
import type {IGroceryCreateItem} from "../api/types/requests/grocery/CreateGroceryItem.ts";
import type {IGroceryDetail} from "../types/IGroceryDetail.ts";
import type {IPayloadGroceryItemUpdate} from "../api/types/requests/grocery/UpdateGroceryItem.ts";
import type {IGroceryFilterParams} from "../api/types/requests/grocery/GroceryFilterParams.ts";
import {AppToast} from "../components/common/AppToast.tsx";
import {BaseError} from "../api/exceptions/baseExceptions.ts";
import {Logger} from "../utility/logger.ts";
import {handleGroceryStoreException} from "../api/exceptions/handleGroceryStoreExceptions.ts";

const logger = new Logger("GroceryStore");

interface IGroceryState {
    groceries: IGroceryListItem[];
    grocery: IGroceryDetail | null;
    isLoading: boolean;
    error: string | null;

    // actions
    fetchGroceries: (filters?: IGroceryFilterParams) => Promise<void>;
    addGroceries: (newItem: IGroceryCreateItem) => Promise<void>;
    getGroceryDetail: (grocery_id: string) => Promise<void>;
    updateGroceryDetail: (grocery_id: string, payload: IPayloadGroceryItemUpdate) => Promise<void>;
    deleteGroceryItem: (grocery_id: string) => Promise<void>;
    bulkUpdateShouldIncludeItems: (grocery_ids: string[], should_include: boolean) => Promise<void>;
}


const useGroceryStore = create<IGroceryState>((set) => ({
    groceries: [],
    isLoading: false,
    grocery: null,
    error: null,
    fetchGroceries: async (filters?: IGroceryFilterParams) => {
        set({isLoading: true, error: null});
        try {
            const data = await getGroceries(filters);
            set({groceries: data, isLoading: false});
        } catch (err) {
            logger.error(err as string);
            set({isLoading: false});
        }
    },
    addGroceries: async (newItem: IGroceryCreateItem) => {
        try {
            await createGroceries(newItem);
            set({isLoading: false});
        } catch (err) {
            handleGroceryStoreException(err, set);
        }
    },
    getGroceryDetail: async (grocery_id: string) => {
        set({grocery: null, isLoading: true});
        try {
            const data = await getGroceryDetail(grocery_id);
            set({grocery: data, isLoading: false});
        } catch (err: unknown) {
            handleGroceryStoreException(err, set);
        }
    },
    updateGroceryDetail: async (grocery_id: string, payload: IPayloadGroceryItemUpdate) => {
        set({isLoading: true})
        try {
            await updateGrocery(grocery_id, payload);
            set({isLoading: false});
        } catch (err: unknown) {
            handleGroceryStoreException(err, set);
        }
    },
    deleteGroceryItem: async (grocery_id: string) => {
        set({isLoading: true});
        try {
            await deleteGrocery(grocery_id);
            set((state) => ({
                groceries: state.groceries.filter((item) => item.id !== grocery_id),
                isLoading: false,
            }));
        } catch (err: unknown) {
            handleGroceryStoreException(err, set);
        }
    },
    bulkUpdateShouldIncludeItems: async (grocery_ids: string[], should_include: boolean) => {
        set({isLoading: true});
        try {
            const updated_items = await bulkUpdateShouldInclude({grocery_ids, should_include});
            const updated_by_id = new Map(updated_items.map((item) => [item.id, item]));
            set((state) => ({
                groceries: state.groceries.map((item) => updated_by_id.get(item.id) ?? item),
                isLoading: false,
            }));
        } catch (err: unknown) {
            if (err instanceof BaseError) {
                logger.error(`Getting error ${err.detail} ${err.status}`);
                AppToast.error(err.message);
            }
            set({isLoading: false});
        }
    }
}));

export default useGroceryStore;