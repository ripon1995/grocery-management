import type {IUserLoginPayload} from "../api/types/requests/auth/UserLoginPayload.ts";
import {create} from "zustand";
import {persist, createJSONStorage} from 'zustand/middleware';
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


const useAuthStore = create<IUserAuthState>()(
    persist(
        (set) => ({
            token: null,
            isLoading: false,
            error: null,
            login: async (payload: IUserLoginPayload) => {
                set({isLoading: true, error: null}); // Start loading
                try {
                    const tokenData = await login(payload);
                    set({token: tokenData, isLoading: false});
                } catch (err) {
                    if (err instanceof BaseError) set({error: err.message});
                    log.debug(`error getting here : ${err}`);
                    set({isLoading: false});
                }
            },
            resetError: () => set({error: null})
        }),
        {
            name: 'auth-storage', // Key name in localStorage
            storage: createJSONStorage(() => localStorage),
        }
    )
);

export default useAuthStore;