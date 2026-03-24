import type {IUserLoginPayload} from "../api/types/requests/auth/UserLoginPayload.ts";
import {create} from "zustand";
import {login} from "../api/endpoints/AuthApi.ts";

interface IUserAuthState {
    access_token: string | null;
    refresh_token: string | null;
    isLoading: boolean;
    error: string | null;
    // actions
    login: (payload: IUserLoginPayload) => Promise<void>;
}


const useAuthStore = create<IUserAuthState>((set) => ({
    access_token: null,
    refresh_token: null,
    isLoading: false,
    error: null,
    login: async (payload: IUserLoginPayload) => {
        try {
            await login(payload);
            set({isLoading: false});
        } catch (err) {
            // TODO -> add error handler like delete grocery
            console.log(err);
            set({isLoading: false});
        }
    }
}));

export default useAuthStore;