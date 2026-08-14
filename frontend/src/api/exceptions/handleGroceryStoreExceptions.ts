import {InvalidUUIDError, NotFoundError} from "./customException.ts";
import {BaseException} from "./baseExceptions.ts";
import {Logger} from "../../utility/logger.ts";
import {AppToast} from "../../components/common/AppToast.tsx";

const logger = new Logger("handleGroceryStoreExceptions");

const handleGroceryStoreException = (err: unknown, set: (state: any) => void) => {
    // Extract error message cleanly
    let message = "An unexpected error occurred";

    if (
        err instanceof NotFoundError ||
        err instanceof InvalidUUIDError ||
        err instanceof BaseException
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

export {handleGroceryStoreException};