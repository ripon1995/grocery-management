export interface BaseErrorPayload {
    status: string;
    error_code: string
    message: string;
    detail: string;
}

export interface IApiErrorResponse {
    success: boolean;
    error: BaseErrorPayload;
}


export class BaseError extends Error implements BaseErrorPayload {
    status: string = 'Fail';
    error_code: string = 'INTERNAL_SERVER_ERROR';
    message: string = 'Something went wrong on our end.';
    detail: string = 'No additional details provided.';

    constructor(data?: Partial<BaseErrorPayload>) {
        super(data?.message || 'Something went wrong on our end.');
        this.name = 'BaseError';
        if (data) {
            this.status = data?.status || this.status;
            this.error_code = data?.error_code || this.error_code;
            this.message = data?.message || this.message;
            this.detail = data?.detail || this.detail;
        }
    }

    // Helper method to create directly from the backend envelope
    static fromApiResponse(responseData?: IApiErrorResponse): BaseError {
        return new BaseError(responseData?.error);
    }
}