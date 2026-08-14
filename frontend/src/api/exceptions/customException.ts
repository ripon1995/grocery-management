// --- Specific Error Subclasses ---


import {BaseException, type IBaseException} from "./baseExceptions.ts";

export class NotFoundError extends BaseException {
    constructor(data?: Partial<IBaseException>) {
        super(data);
        this.name = 'NotFoundError';
    }
}


export class InvalidUUIDError extends BaseException {
    constructor(data?: Partial<IBaseException>) {
        super(data);
        this.name = 'InvalidUUIDError';
    }
}


export class UnauthorizedException extends BaseException {
    constructor(data?: Partial<IBaseException>) {
        super(data);
        this.name = 'UnauthorizedException';
    }

}