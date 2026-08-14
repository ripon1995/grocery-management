// --- Factory Function ---
import {BaseException, type IBaseException} from "./baseExceptions.ts";
import {InvalidUUIDError, NotFoundError, UnauthorizedException} from "./customException.ts";
import ERROR_CODES from "../../constants/errorCodes.ts";


export function toBaseError(payload?: IBaseException): BaseException {
    if (!payload) {
        return new BaseException();
    }

    const code = payload?.error_code?.toLocaleLowerCase()
    switch (code) {
        case ERROR_CODES.RESOURCE_NOT_FOUND:
            return new NotFoundError(payload);
        case ERROR_CODES.INVALID_UUID:
            return new InvalidUUIDError(payload);
        case ERROR_CODES.UNAUTHORIZED:
            return new UnauthorizedException(payload);
        default:
            return new BaseException(payload);
    }
}