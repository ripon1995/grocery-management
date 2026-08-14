// --- Factory Function ---
import {BaseError, type BaseErrorPayload} from "./baseExceptions.ts";
import {NotFoundError} from "./customException.ts";

export function toBaseError(payload?: BaseErrorPayload): BaseError {
    if (!payload) {
        return new BaseError();
    }

    const code = payload?.error_code?.toLocaleLowerCase()
    switch (code) {
        case 'resource_not_found':
            return new NotFoundError(payload);
        default:
            return new BaseError(payload);
    }
}