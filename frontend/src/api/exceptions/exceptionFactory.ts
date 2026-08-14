// --- Factory Function ---
import {BaseError, type BaseErrorPayload} from "./baseExceptions.ts";
import {InvalidUUIDError, NotFoundError} from "./customException.ts";
import ERROR_CODES from "../../constants/errorCodes.ts";


export function toBaseError(payload?: BaseErrorPayload): BaseError {
    if (!payload) {
        return new BaseError();
    }

    const code = payload?.error_code?.toLocaleLowerCase()
    switch (code) {
        case ERROR_CODES.RESOURCE_NOT_FOUND:
            return new NotFoundError(payload);
        case ERROR_CODES.INVALID_UUID:
            return new InvalidUUIDError(payload);
        default:
            return new BaseError(payload);
    }
}