import type {IUserLoginPayload} from "../api/types/requests/auth/UserLoginPayload.ts";
import {create} from "zustand";
import {login} from "../api/endpoints/AuthApi.ts";
import log from "loglevel";
import type {IToken} from "../types/IToken.ts";
import {BaseError} from "../api/types/common.ts";

interface IUserAuthState {
    token: IToken | null
    isLoading: boolean;
    error: string | null;
    // actions
    login: (payload: IUserLoginPayload) => Promise<void>;
    resetError: () => void;
}


const useAuthStore = create<IUserAuthState>((set) => ({
    token: null,
    isLoading: false,
    error: null,
    login: async (payload: IUserLoginPayload) => {
        try {
            const tokenData = await login(payload);
            set({
                token: tokenData,
                isLoading: false
            });
        } catch (err) {
            if (err instanceof BaseError) {
                set({error: err.message})
            }
            log.debug(`error getting here : ${err}`);
            set({isLoading: false});
        }
    },
    resetError: () => set({error: null})
}));

export default useAuthStore;