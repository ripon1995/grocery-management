import axiosInstance from "../axiosInstance.ts";
import API_ENDPOINTS from "../../constants/apiEndpoints.ts";
import type {IUserLoginPayload} from "../types/requests/auth/UserLoginPayload.ts";
import type {IUserLoginResponse} from "../types/responses/UserLoginResponse.ts";
import type {IApiResponse} from "../../types/IApiResponse.ts";


export const login = async (payload: IUserLoginPayload): Promise<IUserLoginResponse> => {
    const response = await axiosInstance.post<IApiResponse<IUserLoginResponse>>(API_ENDPOINTS.AUTH.LOGIN, payload);
    return response.data.data;
}
