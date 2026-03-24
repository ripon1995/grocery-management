const GROCERY_APIS = {
    GROCERY_LIST: '/api/groceries/',
    GROCERY_ADD: '/api/groceries/',
    GROCERY_DETAIL: '/api/groceries/:id',
    GROCERY_UPDATE: '/api/groceries/:id',
    GROCERY_DELETE: '/api/groceries/:id',
}

const AUTH_APIS = {
    LOGIN: '/api/auth/login'
};


const API_ENDPOINTS = {
    GROCERY: GROCERY_APIS,
    AUTH: AUTH_APIS
} as const;

export default API_ENDPOINTS;