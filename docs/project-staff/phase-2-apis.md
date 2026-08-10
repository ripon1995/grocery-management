Learning Tasks:

# Document every endpoint in your current backend with its HTTP method and purpose. Categorize them: which are public? which should be private?

## Grocery apis

1. GET: /api/groceries: list (public api) [HTTP]
2. POST: /api/groceries: create (private api) [HTTP]
3. GET: /api/groceries/{grocery_id}: detail (public api) [HTTP]
4. PUT: /api/groceries/{grocery_id}: update (private api) [HTTP]
5. DELETE: /api/groceries/{grocery_id}: delete (private api) [HTTP]
6. PATCH: /api/groceries/bulk/should-include: bulk update (private api) [HTTP]

## Auth apis

1. POST: /api/auth/register: create (public api) [HTTP]
2. POST: /api/auth/login: login (public api) [HTTP]
3. POST: /api/auth/token-refresh: refresh (public api) [HTTP]

# Draw a flow diagram: Browser → React → FastAPI → Supabase → back

## Flow of a public api: grocery list api

Start → Browser → Index.html → main.tsx → App.tsx → HomePage.tsx → fetchGroceries () [useGroceryStore.ts] → getGroceries
() [GroceryApi.ts] → main.py → api/router.py → grocery/router.py → service.py → repository.py → Supabase → repository.py → service.py →
grocery/router.py → getGroceries () [GroceryApi.ts] → fetchGroceries () [useGroceryStore.ts] → HomePage.tsx (data is
visible now) → End

## Flow of a private api: grocery update api

Start → Browser → Index.html → main.tsx → App.tsx → Homepage.tsx → edit option clicked from a list item action →
UpdateGroceryPage.tsx → Show grocery detail in form → change in form data → click save button → action
triggered [handleSave] → updateGroceryDetail [useGroceryStore.ts] → updateGrocery [GroceryApi.ts] → axiosInstance.ts
(attaches Bearer token) → main.py → api/router.py → grocery/router.py → get_current_user → token verification →
update_grocery [service.py] → update_grocery [repository.py] → service.py → Supabase → repository.py →
grocery/router.py → updateGrocery [GroceryApi.ts] → updateGroceryDetail [useGroceryStore.ts] → UpdateGroceryPage.tsx
(navigates back; errors shown via toast) → End