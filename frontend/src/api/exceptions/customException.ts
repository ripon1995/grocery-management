// --- Specific Error Subclasses ---


import {BaseException, type IBaseError} from "./baseExceptions.ts";

export class NotFoundError extends BaseException {
    constructor(data?: Partial<IBaseError>) {
        super(data);
        this.name = 'NotFoundError';
    }
}


export class InvalidUUIDError extends BaseException {
    constructor(data?: Partial<IBaseError>) {
        super(data);
        this.name = 'InvalidUUIDError';
    }
}


export class UnauthorizedException extends BaseException {
    constructor(data?: Partial<IBaseError>) {
        super(data);
        this.name = 'UnauthorizedException';
    }

}