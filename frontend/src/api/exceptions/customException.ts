// --- Specific Error Subclasses ---


import {BaseError, type BaseErrorPayload} from "./baseExceptions.ts";

export class NotFoundError extends BaseError {
    constructor(data?: Partial<BaseErrorPayload>) {
        super(data);
        this.name = 'NotFoundError';
    }
}


export class InvalidUUIDError extends BaseError {
    constructor(data?: Partial<BaseErrorPayload>) {
        super(data);
        this.name = 'InvalidUUIDError';
    }
}


export class UnauthorizedException extends BaseError {
    constructor(data?: Partial<BaseErrorPayload>) {
        super(data);
        this.name = 'UnauthorizedException';
    }

}