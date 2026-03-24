import axiosInstance from "../axiosInstance.ts";
import API_ENDPOINTS from "../../constants/apiEndpoints.ts";
import type {IUserLoginPayload} from "../types/requests/auth/UserLoginPayload.ts";


export const login = async (payload: IUserLoginPayload): Promise<void> => {
    await axiosInstance.post<void>(API_ENDPOINTS.AUTH.LOGIN, payload);
    return;
}
