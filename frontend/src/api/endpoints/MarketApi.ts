import axiosInstance from "../axiosInstance.ts";
import API_ENDPOINTS from "../../constants/apiEndpoints.ts";
import type {IApiResponse} from "../../types/IApiResponse.ts";
import type {IMarketExploreJob, IMarketExploreJobStatus} from "../../types/IMarketExplore.ts";
import type {IMarketExplorePayload} from "../types/requests/market/MarketExplorePayload.ts";
import {BaseException} from "../exceptions/baseExceptions.ts";

const POLL_INTERVAL_MS = 1_000;
const MAX_WAIT_MS = 180_000;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// The worker does the Gemini calls, so this answers at once with a job to poll
export const exploreMarket = async (payload: IMarketExplorePayload): Promise<IMarketExploreJob> => {
    const response = await axiosInstance.post<IApiResponse<IMarketExploreJob>>(
        API_ENDPOINTS.MARKET.MARKET_EXPLORE,
        payload,
    );
    return response.data.data;
}

export const getExploreJob = async (jobId: string): Promise<IMarketExploreJobStatus> => {
    const response = await axiosInstance.get<IApiResponse<IMarketExploreJobStatus>>(
        API_ENDPOINTS.MARKET.MARKET_EXPLORE_JOB(jobId),
    );
    return response.data.data;
}

/**
 * Poll the job every second until it's done or failed, passing each poll to onProgress.
 * Returns the finished job, or null once isCancelled() is true (the job keeps running in the worker).
 */
export const waitForExploreJob = async (
    jobId: string,
    onProgress: (job: IMarketExploreJobStatus) => void,
    isCancelled: () => boolean,
): Promise<IMarketExploreJobStatus | null> => {
    const giveUpAt = Date.now() + MAX_WAIT_MS;
    while (Date.now() < giveUpAt) {
        const job = await getExploreJob(jobId);
        if (isCancelled()) return null;
        onProgress(job);
        if (job.status === 'done' || job.status === 'failed') return job;

        await sleep(POLL_INTERVAL_MS);
        if (isCancelled()) return null;
    }
    throw new BaseException({
        message: 'Still running, try again later',
        detail: `Explore job ${jobId} didn't finish within ${MAX_WAIT_MS / 1000} s`,
    });
}
