export interface BaseErrorResponse {
    status_code: number;
    error_code: string
    message: string;
    detail: string;
}


export class BaseError implements BaseErrorResponse {
    status_code: number = 500;
    error_code: string = 'INTERNAL_SERVER_ERROR';
    message: string = 'Something went wrong on our end.';
    detail: string = 'No additional details provided.';

    constructor(data: BaseErrorResponse) {
        this.status_code = data.status_code;
        this.error_code = data.error_code;
        this.message = data.message;
        this.detail = data.detail;
    }
}