const ERROR_CODES = {
    RESOURCE_NOT_FOUND: "resource_not_found",
    INVALID_UUID: "invalid_uuid",
    UNAUTHORIZED: "unauthorized",
}

type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];
export {ERROR_CODES};
export type {ErrorCode};