import axiosInstance from "../axiosInstance.ts";
import API_ENDPOINTS from "../../constants/apiEndpoints.ts";
import type {IApiResponse} from "../../types/IApiResponse.ts";
import type {IMarketExploreResult} from "../../types/IMarketExplore.ts";
import type {IMarketExplorePayload} from "../types/requests/market/MarketExplorePayload.ts";

// The backend asks Gemini (with web search) once per item, one after another,
// so this takes far longer than the default 5s timeout
const EXPLORE_TIMEOUT_MS = 120_000;

export const exploreMarket = async (payload: IMarketExplorePayload): Promise<IMarketExploreResult> => {
    const response = await axiosInstance.post<IApiResponse<IMarketExploreResult>>(
        API_ENDPOINTS.MARKET.MARKET_EXPLORE,
        payload,
        {timeout: EXPLORE_TIMEOUT_MS},
    );
    return response.data.data;
}
