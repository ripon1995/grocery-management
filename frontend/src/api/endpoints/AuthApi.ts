import axiosInstance from "../axiosInstance.ts";
import API_ENDPOINTS from "../../constants/apiEndpoints.ts";
import type {IUserLoginPayload} from "../types/requests/auth/UserLoginPayload.ts";
import type {IToken} from "../../types/IToken.ts";


export const login = async (payload: IUserLoginPayload): Promise<IToken> => {
    const response = await axiosInstance.post<IToken>(API_ENDPOINTS.AUTH.LOGIN, payload);
    return response.data;
}
