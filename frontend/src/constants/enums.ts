export const GroceryType = {
    WEIGHT: 'weight',
    SACK: 'sack',
    CAN: 'can',
    PIECE: 'piece',
    PACKET: 'packet',
    BOTTLE: 'bottle'
} as const;
export type GroceryType = typeof GroceryType[keyof typeof GroceryType];

export const GroceryStockStatus = {
    IN_STOCK: 'in_stock',
    BELOW_STOCK: 'below_stock'
} as const;
export type GroceryStockStatus = typeof GroceryStockStatus[keyof typeof GroceryStockStatus];

export const Seller = {
    MEENA: 'meena',
    SHWAPNO: 'shwapno',
    LOCAL: 'local',
    COMILLA: 'comilla',
    DEFAULT: 'default',
    AGORA: 'agora',
    ONLINE: 'online'
} as const;
export type Seller = typeof Seller[keyof typeof Seller];

export const GroceryCategory = {
    TOILETRIES: 'toiletries',
    FOOD: 'food',
    COOKIES: 'cookies',
    OIL: 'oil',
    OTHER: 'other'
} as const;
export type GroceryCategory = typeof GroceryCategory[keyof typeof GroceryCategory];


export const YesNoChoice = {
    YES: 'yes',
    NO: 'no'
}