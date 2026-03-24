export interface BaseErrorResponse {
    status: string;
    error_code: string
    message: string;
    detail: string;
}


export class BaseError implements BaseErrorResponse {
    status: string = 'Fail';
    error_code: string = 'INTERNAL_SERVER_ERROR';
    message: string = 'Something went wrong on our end.';
    detail: string = 'No additional details provided.';

    constructor(data?: BaseErrorResponse) {
        this.status = data?.status || this.status;
        this.error_code = data?.error_code || this.error_code;
        this.message = data?.message || this.message;
        this.detail = data?.detail || this.detail;
    }
}