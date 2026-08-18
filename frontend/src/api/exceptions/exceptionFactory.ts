// --- Factory Function ---
import {BaseException, type IBaseException} from "./baseExceptions.ts";
import {InvalidUUIDError, NotFoundError, UnauthorizedException} from "./customException.ts";
import {ERROR_CODES, type ErrorCode} from "../../constants/errorCodes.ts";


const ERROR_FACTORY: Record<ErrorCode, (payload: IBaseException) => BaseException> = {
    [ERROR_CODES.INVALID_UUID]: (payload) => new InvalidUUIDError(payload),
    [ERROR_CODES.RESOURCE_NOT_FOUND]: (payload) => new NotFoundError(payload),
    [ERROR_CODES.UNAUTHORIZED]: (payload) => new UnauthorizedException(payload),
}


function toBaseError(payload?: IBaseException): BaseException {
    if (!payload) return new BaseException();
    const code = payload.error_code?.toLocaleLowerCase() as ErrorCode;
    return (ERROR_FACTORY[code] ?? ((p: IBaseException) => new BaseException(p)))(payload);
}

export {toBaseError}