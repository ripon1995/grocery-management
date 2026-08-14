import {BaseError} from "./baseExceptions.ts";
import {Logger} from "../../utility/logger.ts";
import {AppToast} from "../../components/common/AppToast.tsx";
import {UnauthorizedException} from "./customException.ts";

const logger = new Logger("handleGroceryStoreExceptions");

const handleAuthStoreException = (err: unknown, set: (state: any) => void) => {
    // Extract error message cleanly
    let message = "An unexpected error occurred";

    if (
        err instanceof UnauthorizedException ||
        err instanceof BaseError
    ) {
        message = err.message;
    } else if (err instanceof Error) {
        message = err.message;
    }

    // 1. Log error
    logger.error(message);

    // 2. Show toast
    AppToast.error(message);

    // 3. Update store state
    set({error: message, isLoading: false});
};

export {handleAuthStoreException};