export interface IBaseError {
    status: string;
    error_code: string
    message: string;
    detail: string;
}

export interface IApiErrorResponse {
    success: boolean;
    error: IBaseError;
}

export class BaseException extends Error implements IBaseError {
    status: string = 'Fail';
    error_code: string = 'INTERNAL_SERVER_ERROR';
    message: string = 'Something went wrong.';
    detail: string = 'No additional details provided.';

    constructor(data?: Partial<IBaseError>) {
        super(data?.message || 'Something went wrong.');
        this.name = 'BaseError';
        if (data) {
            this.status = data?.status || this.status;
            this.error_code = data?.error_code || this.error_code;
            this.message = data?.message || this.message;
            this.detail = data?.detail || this.detail;
        }
    }
}
