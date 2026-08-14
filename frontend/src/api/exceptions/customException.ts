// --- Specific Error Subclasses ---


import {BaseError, type IBaseError} from "./baseExceptions.ts";

export class NotFoundError extends BaseError {
    constructor(data?: Partial<IBaseError>) {
        super(data);
        this.name = 'NotFoundError';
    }
}


export class InvalidUUIDError extends BaseError {
    constructor(data?: Partial<IBaseError>) {
        super(data);
        this.name = 'InvalidUUIDError';
    }
}


export class UnauthorizedException extends BaseError {
    constructor(data?: Partial<IBaseError>) {
        super(data);
        this.name = 'UnauthorizedException';
    }

}