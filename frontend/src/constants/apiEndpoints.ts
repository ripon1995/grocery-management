const API_V1: string = '/api/v1';
const GROCERIES: string = `${API_V1}/groceries`;
const AUTH: string = `${API_V1}/auth`;

const GROCERY_APIS = {
    GROCERY_LIST: `${GROCERIES}/`,
    GROCERY_ADD: `${GROCERIES}/`,
    GROCERY_DETAIL: `${GROCERIES}/:id`,
    GROCERY_UPDATE: `${GROCERIES}/:id`,
    GROCERY_DELETE: `${GROCERIES}/:id`,
    GROCERY_BULK_SHOULD_INCLUDE: `${GROCERIES}/bulk/should-include`,
}

const AUTH_APIS = {
    LOGIN: `${AUTH}/login`
};


const API_ENDPOINTS = {
    GROCERY: GROCERY_APIS,
    AUTH: AUTH_APIS
} as const;

export default API_ENDPOINTS;