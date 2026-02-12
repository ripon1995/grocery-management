export interface BaseErrorResponse {
    error_code: string;
    message: string;
    details: string;
    status: 'error';
}


export class BaseError implements BaseErrorResponse {
    error_code: string;
    message: string;
    details: string;
    status: 'error';

    constructor(data?: Partial<BaseErrorResponse>) {
        this.error_code = data?.error_code || 'INTERNAL_SERVER_ERROR';
        this.message = data?.message || 'Something went wrong on our end.';
        this.details = data?.details || 'No additional details provided.';
        this.status = 'error';
    }
}