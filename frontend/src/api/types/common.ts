// TODO -> purpose to hold the common staff like the following that will be used in many endpoints

export interface ApiErrorResponse {
    status: 'error';
    message: string;
    code?: string;
    details?: Record<string, string[]>;
}