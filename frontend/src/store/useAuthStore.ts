import type {IUserLoginPayload} from "../api/types/requests/auth/UserLoginPayload.ts";
import {create} from "zustand";
import {persist, createJSONStorage} from 'zustand/middleware';
import {login} from "../api/endpoints/AuthApi.ts";
import log from "loglevel";
import type {IUserLoginResponse} from "../api/types/responses/UserLoginResponse.ts";
import {BaseError} from "../api/types/common.ts";

interface IUserAuthState {
    token: IUserLoginResponse | null
    isLoading: boolean;
    error: string | null;
    // actions
    login: (payload: IUserLoginPayload) => Promise<void>;
    resetError: () => void;
    logout: () => void;
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
            resetError: () => set({error: null}),
            logout: () => set({token: null, isLoading: false, error: null})
        }),
        {
            name: 'auth-storage', // Key name in localStorage
            storage: createJSONStorage(() => localStorage),
        }
    )
);

export default useAuthStore;